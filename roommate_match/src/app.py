"""Textual user interface for the roommate matching project."""

from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Button, DataTable, Footer, Header, Input, Label

from .databaseHelper import (
	add_interest_to_student,
	bootstrap_database_and_system,
	create_roommate_request,
	get_interest_options,
	get_group_status_for_student,
	get_incoming_roommate_requests,
	persist_pending_roommate_requests,
	remove_interest_from_student,
	respond_to_roommate_request,
)
from .roommateRequest import roommateRequest
from .system import RoommateSystem


class LoginApp(App):
	"""A simple login screen with email and password fields."""

	db_connection = None
	system: RoommateSystem | None = None
	current_student = None
	db_connection_error: bool = False
	student_rows: list[tuple[str, str, str]] = []
	selected_student_ids: list[int] = []
	selected_student_id: str | None = None
	request_rows: list[dict[str, object]] = []
	selected_request_id: int | None = None
	request_table_mode: str | None = None
	interest_rows: list[tuple[str, bool]] = []
	selected_interest_title: str | None = None
	group_members: list[dict[str, str]] = []

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
			yield Button("View Group Status", id="make-group-button", variant="primary")
			yield Button("View Roommate Requests", id="view-requests-button", variant="primary")
			yield Button("Change Interests", id="change-interests-button", variant="primary")
			yield Button("Logout", id="logout-button", variant="default")
			yield Button("Save and Exit", id="save-exit-button", variant="error")
			yield Button("Return", id="return-button", variant="default", classes="hidden")
			yield Label("", id="menu-status")
			yield DataTable(id="students-table", classes="hidden")
			yield DataTable(id="requests-table", classes="hidden")
			yield DataTable(id="interests-table", classes="hidden")
			yield Button("Send Roommate Request", id="send-request-button", variant="primary", classes="hidden")
			yield Button("Accept Request", id="accept-request-button", variant="primary", classes="hidden")
			yield Button("Reject Request", id="reject-request-button", variant="error", classes="hidden")
			yield Label("", id="group-details", classes="hidden")
		yield Footer()

	def on_mount(self) -> None:
		try:
			self.db_connection, self.system = bootstrap_database_and_system()
			self.db_connection_error = False
		except Exception:
			self.db_connection = None
			self.system = RoommateSystem()
			self.db_connection_error = True
		self.query_one("#students-table", DataTable).cursor_type = "row"
		self.query_one("#requests-table", DataTable).cursor_type = "row"
		self.query_one("#interests-table", DataTable).cursor_type = "row"
		self.query_one("#email", Input).focus()

	def on_unmount(self) -> None:
		if self.db_connection is not None:
			persist_pending_roommate_requests(self.db_connection)
			self.db_connection.close()

	def on_button_pressed(self, event: Button.Pressed) -> None:
		if event.button.id == "login-button":
			self._submit_login()
		elif event.button.id == "view-students-button":
			self._show_students_table()
		elif event.button.id == "return-button":
			self._return_to_menu()
		elif event.button.id == "make-group-button":
			self._show_group_status_menu()
		elif event.button.id == "view-requests-button":
			self._show_roommate_requests_menu()
		elif event.button.id == "change-interests-button":
			self._show_change_interests_menu()
		elif event.button.id == "logout-button":
			self._logout()
		elif event.button.id == "save-exit-button":
			self._save_and_exit()
		elif event.button.id == "send-request-button":
			self._send_roommate_request()
		elif event.button.id == "accept-request-button":
			self._respond_to_selected_request(True)
		elif event.button.id == "reject-request-button":
			self._respond_to_selected_request(False)

	def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
		if event.data_table.id == "students-table":
			self._handle_student_row_selection(event.cursor_row)
		elif event.data_table.id == "requests-table":
			self._handle_request_row_selection(event.cursor_row)
		elif event.data_table.id == "interests-table":
			self._handle_interest_row_selection(event.cursor_row)

	def on_data_table_cell_selected(self, event: DataTable.CellSelected) -> None:
		if event.data_table.id == "requests-table":
			self._handle_request_row_selection(event.coordinate.row)

	def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
		row_index = event.data_table.cursor_row
		if row_index < 0:
			return

		if event.data_table.id == "requests-table":
			self._handle_request_row_selection(row_index)
		elif event.data_table.id == "interests-table":
			self._preview_interest_row(row_index)

	def on_data_table_cell_highlighted(self, event: DataTable.CellHighlighted) -> None:
		row_index = event.coordinate.row
		if row_index < 0:
			return

		if event.data_table.id == "requests-table":
			self._handle_request_row_selection(row_index)
		elif event.data_table.id == "interests-table":
			self._preview_interest_row(row_index)

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

		self.current_student = student
		self.group_members = []
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
			if self.current_student is not None and student.id == self.current_student.id:
				continue
			interests = ", ".join(student.interests) if student.interests else "No interests"
			rows.append((str(student.id), str(student.name), interests))
		return rows

	def _show_students_table(self) -> None:
		status = self.query_one("#menu-status", Label)
		table = self.query_one("#students-table", DataTable)
		requests_table = self.query_one("#requests-table", DataTable)
		interests_table = self.query_one("#interests-table", DataTable)
		group_details = self.query_one("#group-details", Label)

		if self.db_connection_error or self.system is None:
			status.update("Unable to connect to app.db.")
			return

		students = self._fetch_students_with_interests()
		self.student_rows = students
		self.selected_student_ids = []
		self.selected_student_id = None
		self.selected_request_id = None
		self.request_table_mode = None
		self._render_students_table()

		if not students:
			status.update("No students found in the database.")
		else:
			status.update("Student list loaded. Click a student to show actions.")

		self._set_students_view_mode(True)
		requests_table.add_class("hidden")
		interests_table.add_class("hidden")
		group_details.add_class("hidden")
		self.query_one("#accept-request-button", Button).add_class("hidden")
		self.query_one("#reject-request-button", Button).add_class("hidden")
		self.query_one("#send-request-button", Button).add_class("hidden")
		table.remove_class("hidden")
		table.focus()

	def _show_group_status_menu(self, info_message: str | None = None) -> None:
		status = self.query_one("#menu-status", Label)
		table = self.query_one("#students-table", DataTable)
		requests_table = self.query_one("#requests-table", DataTable)
		interests_table = self.query_one("#interests-table", DataTable)
		send_button = self.query_one("#send-request-button", Button)
		accept_button = self.query_one("#accept-request-button", Button)
		reject_button = self.query_one("#reject-request-button", Button)
		group_details = self.query_one("#group-details", Label)

		table.add_class("hidden")
		requests_table.add_class("hidden")
		interests_table.add_class("hidden")
		send_button.add_class("hidden")
		accept_button.add_class("hidden")
		reject_button.add_class("hidden")
		self.request_table_mode = None
		self.selected_request_id = None
		self._set_students_view_mode(True)

		if self.current_student is not None and self.db_connection is not None:
			self.group_members = get_group_status_for_student(self.db_connection, int(self.current_student.id))

		if not self.group_members:
			group_details.update("No group yet. Select a student in View Other Students and send a roommate request.")
			status.update(info_message or "No group created yet.")
		else:
			group_details.update(self._format_group_status())
			status.update(info_message or "Group status loaded.")

		group_details.remove_class("hidden")

	def _show_roommate_requests_menu(self) -> None:
		status = self.query_one("#menu-status", Label)
		students_table = self.query_one("#students-table", DataTable)
		requests_table = self.query_one("#requests-table", DataTable)
		interests_table = self.query_one("#interests-table", DataTable)
		send_button = self.query_one("#send-request-button", Button)
		accept_button = self.query_one("#accept-request-button", Button)
		reject_button = self.query_one("#reject-request-button", Button)
		group_details = self.query_one("#group-details", Label)

		if self.current_student is None or self.db_connection is None:
			status.update("No logged-in student found.")
			return

		self.request_rows = get_incoming_roommate_requests(self.db_connection, int(self.current_student.id))
		self.selected_request_id = None
		self.request_table_mode = "incoming"

		requests_table.clear(columns=True)
		requests_table.add_columns("Request ID", "From", "Group Members", "Status")
		for request_row in self.request_rows:
			sender_name = self._student_name_from_id(int(request_row["sender_id"]))
			member_names = ", ".join(self._student_name_from_id(member_id) for member_id in request_row["receiver_ids"])
			requests_table.add_row(
				str(request_row["request_id"]),
				sender_name,
				member_names,
				str(request_row["status"]).capitalize(),
			)

		students_table.add_class("hidden")
		interests_table.add_class("hidden")
		group_details.add_class("hidden")
		send_button.add_class("hidden")
		accept_button.add_class("hidden")
		reject_button.add_class("hidden")
		self._set_students_view_mode(True)

		if not self.request_rows:
			status.update("No roommate requests found.")
		else:
			status.update("Select a request to show response actions.")

		requests_table.remove_class("hidden")
		requests_table.focus()

	def _show_change_interests_menu(self, info_message: str | None = None) -> None:
		status = self.query_one("#menu-status", Label)
		students_table = self.query_one("#students-table", DataTable)
		requests_table = self.query_one("#requests-table", DataTable)
		interests_table = self.query_one("#interests-table", DataTable)
		send_button = self.query_one("#send-request-button", Button)
		accept_button = self.query_one("#accept-request-button", Button)
		reject_button = self.query_one("#reject-request-button", Button)
		group_details = self.query_one("#group-details", Label)

		if self.current_student is None or self.db_connection is None:
			status.update("No logged-in student found.")
			return

		interest_options = self._get_available_interest_titles()
		current_interest_titles = set(self.current_student.interests)

		self.interest_rows = [
			(title, title in current_interest_titles)
			for title in sorted(interest_options, key=lambda interest_title: interest_title.lower())
		]
		self.selected_interest_title = None

		interests_table.clear(columns=True)
		interests_table.add_columns("Interest", "In Your Profile")
		for title, selected in self.interest_rows:
			interests_table.add_row(title, "Yes" if selected else "No")

		students_table.add_class("hidden")
		requests_table.add_class("hidden")
		group_details.add_class("hidden")
		send_button.add_class("hidden")
		accept_button.add_class("hidden")
		reject_button.add_class("hidden")
		self._set_students_view_mode(True)

		if not self.interest_rows:
			status.update("No interests found.")
		elif info_message is not None:
			status.update(info_message)
		else:
			status.update("Click an interest to select it, then click it again to toggle Yes/No.")

		interests_table.remove_class("hidden")
		interests_table.focus()

	def _format_group_status(self) -> str:
		lines = ["Current Group Status:"]
		for member in self.group_members:
			member_id = int(member["id"])
			member_name = self._student_name_from_id(member_id)
			lines.append(f"- {member_name}: {member['status']}")
		return "\n".join(lines)

	def _render_students_table(self) -> None:
		table = self.query_one("#students-table", DataTable)
		table.clear(columns=True)
		table.add_columns("Selected", "Student ID", "Student Name", "Interests")

		selected_ids = set(self.selected_student_ids)
		for student_id, student_name, interests in self.student_rows:
			selected_text = "Yes" if int(student_id) in selected_ids else "No"
			table.add_row(selected_text, str(student_id), student_name, interests)

	def _add_or_update_group_member(self, student_id: str, student_name: str, status: str) -> None:
		for member in self.group_members:
			if member["id"] == student_id:
				member["status"] = status
				return

		self.group_members.append({"id": student_id, "name": student_name, "status": status})

	def _selected_student_name(self) -> str | None:
		names = self._selected_student_names()
		return names[0] if names else None

	def _selected_student_names(self) -> list[str]:
		return [self._student_name_from_id(student_id) for student_id in self.selected_student_ids]

	def _student_name_from_id(self, student_id: int) -> str:
		if self.system is not None:
			student = self.system.getStudentById(student_id)
			if student is not None:
				return student.name
		return f"Student {student_id}"

	def _set_students_view_mode(self, enabled: bool) -> None:
		menu_buttons = (
			self.query_one("#view-students-button", Button),
			self.query_one("#make-group-button", Button),
			self.query_one("#view-requests-button", Button),
			self.query_one("#change-interests-button", Button),
			self.query_one("#logout-button", Button),
			self.query_one("#save-exit-button", Button),
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
		requests_table = self.query_one("#requests-table", DataTable)
		interests_table = self.query_one("#interests-table", DataTable)
		status = self.query_one("#menu-status", Label)
		send_button = self.query_one("#send-request-button", Button)
		accept_button = self.query_one("#accept-request-button", Button)
		reject_button = self.query_one("#reject-request-button", Button)
		group_details = self.query_one("#group-details", Label)

		table.add_class("hidden")
		requests_table.add_class("hidden")
		interests_table.add_class("hidden")
		send_button.add_class("hidden")
		accept_button.add_class("hidden")
		reject_button.add_class("hidden")
		group_details.add_class("hidden")
		self.selected_student_id = None
		self.selected_student_ids = []
		self.selected_request_id = None
		self.selected_interest_title = None
		self.request_table_mode = None
		self._set_students_view_mode(False)
		status.update("")

	def _handle_student_row_selection(self, row_index: int) -> None:
		status = self.query_one("#menu-status", Label)
		send_button = self.query_one("#send-request-button", Button)

		if row_index < 0 or row_index >= len(self.student_rows):
			return

		student_id, student_name, _ = self.student_rows[row_index]
		student_id_int = int(student_id)

		if student_id_int in self.selected_student_ids:
			self.selected_student_ids.remove(student_id_int)
			status.update(f"Removed {student_name} from the request group.")
		else:
			if len(self.selected_student_ids) >= 3:
				status.update("You can select up to 3 other students.")
				return
			self.selected_student_ids.append(student_id_int)
			status.update(f"Added {student_name} to the request group.")

		self.selected_student_ids.sort()
		if self.selected_student_ids:
			send_button.remove_class("hidden")
		else:
			send_button.add_class("hidden")
		self._render_students_table()

	def _send_roommate_request(self) -> None:
		status = self.query_one("#menu-status", Label)

		if not self.selected_student_ids:
			status.update("Select at least one student first.")
			return

		if self.current_student is None:
			status.update("No logged-in student found.")
			return

		if self.db_connection is None:
			status.update("Unable to connect to app.db.")
			return

		selected_names = self._selected_student_names()
		new_request = roommateRequest(int(self.current_student.id), *self.selected_student_ids)
		success, message = create_roommate_request(self.db_connection, new_request)
		if not success:
			status.update(message)
			return

		self.selected_student_ids = []
		self._render_students_table()
		self._show_group_status_menu(f"{message} Sent to {', '.join(selected_names)}.")

	def _handle_request_row_selection(self, row_index: int) -> None:
		status = self.query_one("#menu-status", Label)
		accept_button = self.query_one("#accept-request-button", Button)
		reject_button = self.query_one("#reject-request-button", Button)

		if row_index < 0 or row_index >= len(self.request_rows):
			return

		selected_row = self.request_rows[row_index]
		self.selected_request_id = int(selected_row["request_id"])

		request_model = selected_row["request"]
		if isinstance(request_model, roommateRequest):
			sender_id = request_model.getSenderId()
		else:
			sender_id = "Unknown"

		accept_button.remove_class("hidden")
		reject_button.remove_class("hidden")
		status.update(f"Selected request from student {sender_id}. Choose Accept or Reject.")

	def _handle_interest_row_selection(self, row_index: int) -> None:
		if row_index < 0 or row_index >= len(self.interest_rows):
			return

		interest_title, is_in_profile = self.interest_rows[row_index]

		if self.selected_interest_title == interest_title:
			self._toggle_interest_selection(interest_title, is_in_profile)
			return

		self._preview_interest_row(row_index)

	def _preview_interest_row(self, row_index: int) -> None:
		status = self.query_one("#menu-status", Label)

		if row_index < 0 or row_index >= len(self.interest_rows):
			return

		interest_title, is_in_profile = self.interest_rows[row_index]
		self.selected_interest_title = interest_title
		status_text = "currently in" if is_in_profile else "not in"
		status.update(f"Selected {interest_title}. It is {status_text} your profile. Click again to toggle.")

	def _toggle_interest_selection(self, interest_title: str, is_in_profile: bool) -> None:
		if self.current_student is None or self.db_connection is None:
			self.query_one("#menu-status", Label).update("No logged-in student found.")
			return

		if is_in_profile:
			success, message = remove_interest_from_student(
				self.db_connection,
				int(self.current_student.id),
				interest_title,
			)
		else:
			success, message = add_interest_to_student(
				self.db_connection,
				int(self.current_student.id),
				interest_title,
			)

		if success:
			self._update_current_student_interest_state(interest_title, not is_in_profile)
		self.selected_interest_title = None
		self._show_change_interests_menu(message)

	def _respond_to_selected_request(self, accept: bool) -> None:
		status = self.query_one("#menu-status", Label)

		if self.selected_request_id is None:
			status.update("Select a request first.")
			return

		if self.db_connection is None:
			status.update("Unable to connect to app.db.")
			return

		updated = respond_to_roommate_request(
			self.db_connection,
			self.selected_request_id,
			accept,
			int(self.current_student.id) if self.current_student is not None else None,
		)
		if not updated:
			status.update("Could not update request status.")
			return

		result_text = "accepted" if accept else "rejected"
		status.update(f"Request {self.selected_request_id} {result_text}.")
		self._show_roommate_requests_menu()

	def _get_available_interest_titles(self) -> list[str]:
		if self.system is not None and self.system.interest_options:
			return list(self.system.interest_options)

		if self.db_connection is None:
			return []

		options = [title for _, title in get_interest_options(self.db_connection)]
		if self.system is not None:
			self.system.interest_options = list(options)
		return options

	def _update_current_student_interest_state(self, interest_title: str, should_have_interest: bool) -> None:
		if self.current_student is None:
			return

		current_interests = set(self.current_student.interests)
		if should_have_interest:
			current_interests.add(interest_title)
		else:
			current_interests.discard(interest_title)

		self.current_student.interests = sorted(current_interests)

	def _logout(self) -> None:
		login_panel = self.query_one("#login-panel", Container)
		student_menu = self.query_one("#student-menu", Container)
		login_status = self.query_one("#status", Label)
		welcome = self.query_one("#menu-welcome", Label)
		email_input = self.query_one("#email", Input)
		password_input = self.query_one("#password", Input)

		self._return_to_menu()
		self.current_student = None
		self.group_members = []
		self.student_rows = []
		self.selected_student_ids = []
		self.request_rows = []

		welcome.update("")
		email_input.value = ""
		password_input.value = ""
		student_menu.add_class("hidden")
		login_panel.remove_class("hidden")
		login_status.update("Logged out.")
		email_input.focus()

	def _save_and_exit(self) -> None:
		if self.db_connection is not None:
			persist_pending_roommate_requests(self.db_connection)
		self.exit()


def main() -> None:
	LoginApp().run()


if __name__ == "__main__":
	main()
