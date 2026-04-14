"""Textual user interface for the roommate matching project."""

import sqlite3
from pathlib import Path

from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Button, DataTable, Footer, Header, Input, Label


class LoginApp(App):
	"""A simple login screen with email and password fields."""

	db_connection: sqlite3.Connection | None = None
	db_connection_error: bool = False

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
			yield Label("", id="menu-status")
			yield DataTable(id="students-table", classes="hidden")
		yield Footer()

	def on_mount(self) -> None:
		self._connect_database()
		self.query_one("#email", Input).focus()

	def on_unmount(self) -> None:
		if self.db_connection is not None:
			self.db_connection.close()

	def on_button_pressed(self, event: Button.Pressed) -> None:
		if event.button.id == "login-button":
			self._submit_login()
		elif event.button.id == "view-students-button":
			self._show_students_table()
		elif event.button.id == "make-group-button":
			self.query_one("#menu-status", Label).update("Opening group creation...")
		elif event.button.id == "change-preferences-button":
			self.query_one("#menu-status", Label).update("Opening preferences...")

	def action_login(self) -> None:
		self._submit_login()

	def _submit_login(self) -> None:
		email = self.query_one("#email", Input).value.strip()
		password = self.query_one("#password", Input).value
		status = self.query_one("#status", Label)

		if not email or not password:
			status.update("Please enter both an email and password.")
			return

		# TODO: check email and username in database
		status.update(f"Signed in as {email}.")
		self._show_student_menu(email)

	def _show_student_menu(self, email: str) -> None:
		login_panel = self.query_one("#login-panel", Container)
		student_menu = self.query_one("#student-menu", Container)
		welcome = self.query_one("#menu-welcome", Label)

		welcome.update(f"Welcome, {email}")
		login_panel.add_class("hidden")
		student_menu.remove_class("hidden")

	def _connect_database(self) -> None:
		database_path = Path(__file__).resolve().parents[2] / "app.db"
		try:
			self.db_connection = sqlite3.connect(database_path)
			self.db_connection_error = False
		except sqlite3.Error:
			self.db_connection = None
			self.db_connection_error = True

	def _fetch_students_with_interests(self) -> list[tuple[str, str, str]]:
		if self.db_connection is None:
			return []

		query = """
		SELECT
			CAST(s.id AS TEXT) AS student_id,
			s.name,
			COALESCE(GROUP_CONCAT(i.title, ', '), 'No interests') AS interests
		FROM students AS s
		LEFT JOIN students_to_interests AS sti ON sti.student_id = s.id
		LEFT JOIN interests AS i ON i.id = sti.interest_id
		WHERE LOWER(CAST(s.id AS TEXT)) != 'student_id'
		GROUP BY s.id, s.name
		ORDER BY s.name ASC
		"""

		cursor = self.db_connection.cursor()
		rows = cursor.execute(query).fetchall()
		return [(str(row[0]), str(row[1]), str(row[2])) for row in rows]

	def _show_students_table(self) -> None:
		status = self.query_one("#menu-status", Label)
		table = self.query_one("#students-table", DataTable)

		if self.db_connection_error or self.db_connection is None:
			status.update("Unable to connect to app.db.")
			return

		students = self._fetch_students_with_interests()
		table.clear(columns=True)
		table.add_columns("Student ID", "Student Name", "Interests")

		for student_id, student_name, interests in students:
			table.add_row(str(student_id), student_name, interests)

		if not students:
			status.update("No students found in the database.")
		else:
			status.update("Student list loaded.")

		table.remove_class("hidden")


def main() -> None:
	#TODO: load database
	LoginApp().run()


if __name__ == "__main__":
	main()
