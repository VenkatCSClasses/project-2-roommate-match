"""Textual user interface for the roommate matching project."""

from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Button, DataTable, Footer, Header, Input, Label

from .databaseHelper import bootstrap_database_and_system
from .system import RoommateSystem


class LoginApp(App):
	"""A simple login screen with email and password fields."""

	db_connection = None
	system: RoommateSystem | None = None
	db_connection_error: bool = False
	student_rows: list[tuple[str, str, str]] = []
	selected_student_id: str | None = None

	CSS = """
	Screen {
		align: center middle;
	}

	#login-panel {
		width: 100%;
		padding: 2 3;
		border: round $primary;
		background: $panel;
	}

	#student-menu {
		width: 100%;
		padding: 2 3;
		border: round $accent;
		background: $panel;
	}

	#title {
		content-align: center middle;
		text-style: bold;
		margin-bottom: 1;
	}

	Input {
		width: 100%;
		margin: 1 0;
	}

	Button {
		width: 100%;
		margin-top: 1;
	}

	#status {
		margin-top: 1;
		color: $text-muted;
	}

	#menu-status {
		margin-top: 1;
		color: $text-muted;
	}

	#students-table {
		width: 100%;
		height: 12;
		margin-top: 1;
	}

	.hidden {
		display: none;
	}
	"""

	BINDINGS = [("q", "quit", "Quit")]

	def compose(self) -> ComposeResult:
		yield Header()
		with Container(id="login-panel"):
			yield Label("Roommate Match Login", id="title")
			yield Label("Email")
			yield Input(placeholder="Enter email", id="email")
			yield Label("Password")
			yield Input(placeholder="Enter password", password=True, id="password")
			yield Button("Sign in", id="login-button", variant="primary")
			yield Label("", id="status")

		with Container(id="student-menu", classes="hidden"):
			yield Label("Student Menu", id="title")
			yield Label("", id="menu-welcome")
			yield Button("View Other Students", id="view-students-button", variant="primary")
			yield Button("Make Group", id="make-group-button", variant="primary")
			yield Button("Change Preferences", id="change-preferences-button", variant="primary")
			yield Button("Return", id="return-button", variant="default", classes="hidden")
			yield Label("", id="menu-status")
			yield DataTable(id="students-table", classes="hidden")
			yield Button("Send Roommate Request", id="send-request-button", variant="primary", classes="hidden")
		yield Footer()

	def on_mount(self) -> None:
		try:
			self.db_connection, self.system = bootstrap_database_and_system()
			self.db_connection_error = False
		except Exception:
			self.db_connection = None
			self.system = RoommateSystem()
			self.db_connection_error = True
		self.query_one("#email", Input).focus()

	def on_unmount(self) -> None:
		if self.db_connection is not None:
			self.db_connection.close()

	def on_button_pressed(self, event: Button.Pressed) -> None:
		if event.button.id == "login-button":
			self._submit_login()
		elif event.button.id == "view-students-button":
			self._show_students_table()
		elif event.button.id == "return-button":
			self._return_to_menu()
		elif event.button.id == "make-group-button":
			self.query_one("#menu-status", Label).update("Opening group creation...")
		elif event.button.id == "change-preferences-button":
			self.query_one("#menu-status", Label).update("Opening preferences...")
		elif event.button.id == "send-request-button":
			self._send_roommate_request()

	def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
		if event.data_table.id != "students-table":
			return

		self._handle_student_row_selection(event.cursor_row)

	def on_data_table_cell_selected(self, event: DataTable.CellSelected) -> None:
		if event.data_table.id != "students-table":
			return

		self._handle_student_row_selection(event.coordinate.row)

	def action_login(self) -> None:
		self._submit_login()

	def _submit_login(self) -> None:
		email = self.query_one("#email", Input).value.strip()
		password = self.query_one("#password", Input).value
		status = self.query_one("#status", Label)

		if not email or not password:
			status.update("Please enter both an email and password.")
			return

		if self.db_connection_error:
			status.update("Unable to connect to app.db.")
			return

		student = self._authenticate_student(email, password)
		if student is None:
			status.update("Invalid email or password.")
			return

		status.update(f"Signed in as {student.name}.")
		self._show_student_menu(student.name)

	def _show_student_menu(self, email: str) -> None:
		login_panel = self.query_one("#login-panel", Container)
		student_menu = self.query_one("#student-menu", Container)
		welcome = self.query_one("#menu-welcome", Label)

		welcome.update(f"Welcome, {email}")
		login_panel.add_class("hidden")
		student_menu.remove_class("hidden")

	def _authenticate_student(self, email: str, password: str):
		if self.system is None:
			return None

		for student in self.system.students:
			if student.email == email and student.password == password:
				return student
		return None

	def _fetch_students_with_interests(self) -> list[tuple[str, str, str]]:
		if self.system is None:
			return []

		rows: list[tuple[str, str, str]] = []
		for student in sorted(self.system.students, key=lambda s: s.name.lower()):
			interests = ", ".join(student.interests) if student.interests else "No interests"
			rows.append((str(student.id), str(student.name), interests))
		return rows

	def _show_students_table(self) -> None:
		status = self.query_one("#menu-status", Label)
		table = self.query_one("#students-table", DataTable)

		if self.db_connection_error or self.system is None:
			status.update("Unable to connect to app.db.")
			return

		students = self._fetch_students_with_interests()
		self.student_rows = students
		self.selected_student_id = None
		table.clear(columns=True)
		table.add_columns("Student ID", "Student Name", "Interests")

		for student_id, student_name, interests in students:
			table.add_row(str(student_id), student_name, interests)

		if not students:
			status.update("No students found in the database.")
		else:
			status.update("Student list loaded. Select a student and press Enter.")

		self._set_students_view_mode(True)
		self.query_one("#send-request-button", Button).add_class("hidden")
		table.remove_class("hidden")
		table.focus()

	def _set_students_view_mode(self, enabled: bool) -> None:
		menu_buttons = (
			self.query_one("#view-students-button", Button),
			self.query_one("#make-group-button", Button),
			self.query_one("#change-preferences-button", Button),
		)
		return_button = self.query_one("#return-button", Button)

		for button in menu_buttons:
			if enabled:
				button.add_class("hidden")
			else:
				button.remove_class("hidden")

		if enabled:
			return_button.remove_class("hidden")
		else:
			return_button.add_class("hidden")

	def _return_to_menu(self) -> None:
		table = self.query_one("#students-table", DataTable)
		status = self.query_one("#menu-status", Label)
		send_button = self.query_one("#send-request-button", Button)

		table.add_class("hidden")
		send_button.add_class("hidden")
		self.selected_student_id = None
		self._set_students_view_mode(False)
		status.update("")

	def _handle_student_row_selection(self, row_index: int) -> None:
		status = self.query_one("#menu-status", Label)
		send_button = self.query_one("#send-request-button", Button)

		if row_index < 0 or row_index >= len(self.student_rows):
			return

		student_id, student_name, _ = self.student_rows[row_index]
		self.selected_student_id = student_id
		send_button.remove_class("hidden")
		status.update(f"Selected {student_name}. Option: Send roommate request.")

	def _send_roommate_request(self) -> None:
		status = self.query_one("#menu-status", Label)

		if self.selected_student_id is None:
			status.update("Select a student first.")
			return

		status.update(f"Roommate request sent to student {self.selected_student_id}.")


def main() -> None:
	LoginApp().run()


if __name__ == "__main__":
	main()
