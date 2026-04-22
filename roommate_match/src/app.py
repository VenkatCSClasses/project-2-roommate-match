"""Textual user interface for the roommate matching project."""

from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Button, DataTable, Footer, Header, Input, Label

from .databaseHelper import (
	add_interest_to_student,
	bootstrap_database_and_system,
	create_roommate_request,
	get_group_status_for_student,
	get_incoming_roommate_requests,
	get_outgoing_roommate_requests,
	persist_pending_interest_updates,
	persist_pending_roommate_requests,
	persist_students,
	remove_interest_from_student,
	respond_to_roommate_request,
)
from .admin import Admin
from .roommateRequest import roommateRequest
from .system import RoommateSystem


class LoginApp(App):
	"""A simple login screen with email and password fields."""

	db_connection = None
	system: RoommateSystem | None = None
	current_student = None
	current_admin: Admin | None = None
	current_admin_name: str | None = None
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

	#admin-menu {
		width: 100%;
		padding: 2 3;
		border: round $accent;
		background: $panel;
	}

	#admin-create-student-menu {
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

	BINDINGS = []

	def compose(self) -> ComposeResult:
		yield Header()
		with Container(id="login-panel"):
			yield Label("Roommate Match Login", id="title")
			yield Label("Email")
			yield Input(placeholder="Enter email", id="email")
			yield Label("Password")
			yield Input(placeholder="Enter password", password=True, id="password")
			yield Button("Sign in", id="login-button", variant="primary")
			yield Button("Save and Exit", id="login-save-exit-button", variant="error")
			yield Label("", id="status")

		with Container(id="student-menu", classes="hidden"):
			yield Label("Student Menu", id="title")
			yield Label("", id="menu-welcome")
			yield Button("View Other Students", id="view-students-button", variant="primary")
			yield Button("View Request Status", id="view-request-status-button", variant="primary")
			yield Button("View Group Status", id="make-group-button", variant="primary")
			yield Button("Respond to Requests", id="view-requests-button", variant="primary")
			yield Button("Change Interests", id="change-interests-button", variant="primary")
			yield Button("Change Password", id="change-password-button", variant="primary")
			yield Label("Current Password", id="change-password-current-label", classes="hidden")
			yield Input(placeholder="Enter current password", password=True, id="change-password-current-input", classes="hidden")
			yield Label("New Password", id="change-password-new-label", classes="hidden")
			yield Input(placeholder="Enter new password", password=True, id="change-password-new-input", classes="hidden")
			yield Button("Update Password", id="change-password-submit-button", variant="primary", classes="hidden")
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

		with Container(id="admin-menu", classes="hidden"):
			yield Label("Admin Menu", id="title")
			yield Label("", id="admin-menu-welcome")
			yield Button("Create Student", id="admin-create-student-button", variant="primary")
			yield Button("Finalize Pairing", id="admin-finalize-pairing-button", variant="primary")
			yield Button("Logout", id="admin-logout-button", variant="default")
			yield Button("Save and Exit", id="admin-save-exit-button", variant="error")
			yield Label("", id="admin-menu-status")

		with Container(id="admin-create-student-menu", classes="hidden"):
			yield Label("Create Student", id="title")
			yield Label("", id="admin-create-student-welcome")
			yield Label("First Name", id="admin-create-first-name-label")
			yield Input(placeholder="Enter first name", id="admin-create-first-name")
			yield Label("Last Name", id="admin-create-last-name-label")
			yield Input(placeholder="Enter last name", id="admin-create-last-name")
			yield Label("Hometown", id="admin-create-hometown-label")
			yield Input(placeholder="Enter hometown", id="admin-create-hometown")
			yield Label("Email", id="admin-create-email-label")
			yield Input(placeholder="Enter email", id="admin-create-email")
			yield Button("Submit Student", id="admin-create-student-submit-button", variant="primary")
			yield Button("Cancel", id="admin-create-student-cancel-button", variant="default")
			yield Label("", id="admin-create-student-status")
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
			persist_pending_interest_updates(self.db_connection)
			if self.system is not None:
				persist_pending_roommate_requests(self.db_connection, self.system)
				persist_students(self.db_connection, self.system)
			self.db_connection.close()

	def on_button_pressed(self, event: Button.Pressed) -> None:
		if event.button.id == "login-button":
			self._submit_login()
		elif event.button.id == "login-save-exit-button":
			self._save_and_exit()
		elif event.button.id == "view-students-button":
			self._show_students_table()
		elif event.button.id == "view-request-status-button":
			self._show_request_status_menu()
		elif event.button.id == "return-button":
			self._return_to_menu()
		elif event.button.id == "make-group-button":
			self._show_group_status_menu()
		elif event.button.id == "view-requests-button":
			self._show_roommate_requests_menu()
		elif event.button.id == "change-interests-button":
			self._show_change_interests_menu()
		elif event.button.id == "change-password-button":
			self._show_change_password_menu()
		elif event.button.id == "change-password-submit-button":
			self._submit_change_password()
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
		elif event.button.id == "admin-create-student-button":
			self._admin_create_student()
		elif event.button.id == "admin-create-student-submit-button":
			self._admin_submit_create_student()
		elif event.button.id == "admin-create-student-cancel-button":
			self._show_admin_menu(self.current_admin_name or "Admin")
			self.query_one("#admin-menu-status", Label).update("Create Student canceled.")
		elif event.button.id == "admin-finalize-pairing-button":
			self.query_one("#admin-menu-status", Label).update("Finalize Pairing coming soon.")
		elif event.button.id == "admin-logout-button":
			self._logout()
		elif event.button.id == "admin-save-exit-button":
			self._save_and_exit()

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
		if student is not None:
			self.current_student = student
			self.current_admin = None
			self.current_admin_name = None
			self.group_members = []
			status.update(f"Signed in as {student.name}.")
			self._show_student_menu(student.name)
			return

		admin = self._authenticate_admin(email, password)
		if admin is None:
			status.update("Invalid email or password.")
			return

		self.current_student = None
		self.current_admin = admin
		self.current_admin_name = str(admin.name)
		status.update(f"Signed in as admin {admin.name}.")
		self._show_admin_menu(str(admin.name))

	def _show_student_menu(self, email: str) -> None:
		login_panel = self.query_one("#login-panel", Container)
		student_menu = self.query_one("#student-menu", Container)
		admin_menu = self.query_one("#admin-menu", Container)
		welcome = self.query_one("#menu-welcome", Label)

		welcome.update(f"Welcome, {email}")
		admin_menu.add_class("hidden")
		login_panel.add_class("hidden")
		student_menu.remove_class("hidden")

	def _show_admin_menu(self, admin_name: str) -> None:
		login_panel = self.query_one("#login-panel", Container)
		student_menu = self.query_one("#student-menu", Container)
		admin_menu = self.query_one("#admin-menu", Container)
		admin_create_student_menu = self.query_one("#admin-create-student-menu", Container)
		welcome = self.query_one("#admin-menu-welcome", Label)
		admin_status = self.query_one("#admin-menu-status", Label)

		welcome.update(f"Welcome, {admin_name}")
		admin_status.update("")
		admin_create_student_menu.add_class("hidden")
		student_menu.add_class("hidden")
		login_panel.add_class("hidden")
		admin_menu.remove_class("hidden")

	def _authenticate_student(self, email: str, password: str):
		if self.system is None:
			return None

		for student in self.system.students:
			if student.email == email and student.password == password:
				return student
		return None

	def _authenticate_admin(self, email: str, password: str) -> Admin | None:
		if self.system is None:
			return None

		for admin in self.system.admins:
			if str(admin.email) == email and str(admin.password) == password:
				return admin
		return None

	def _admin_create_student(self) -> None:
		status = self.query_one("#admin-create-student-status", Label)
		if self.current_admin is None or self.system is None:
			status.update("No admin account is currently active.")
			return

		admin_menu = self.query_one("#admin-menu", Container)
		admin_create_student_menu = self.query_one("#admin-create-student-menu", Container)
		admin_create_student_welcome = self.query_one("#admin-create-student-welcome", Label)
		admin_create_student_welcome.update(f"Welcome, {self.current_admin_name or 'Admin'}")
		admin_menu.add_class("hidden")
		admin_create_student_menu.remove_class("hidden")
		self.query_one("#admin-create-first-name", Input).focus()
		status.update("Enter first name, last name, hometown, and email.")

	def _admin_submit_create_student(self) -> None:
		status = self.query_one("#admin-create-student-status", Label)
		if self.current_admin is None or self.system is None:
			status.update("No admin account is currently active.")
			return

		first_name = self.query_one("#admin-create-first-name", Input).value.strip()
		last_name = self.query_one("#admin-create-last-name", Input).value.strip()
		hometown = self.query_one("#admin-create-hometown", Input).value.strip()
		email = self.query_one("#admin-create-email", Input).value.strip().lower()

		if not first_name or not last_name or not hometown or not email:
			status.update("Please fill in first name, last name, hometown, and email.")
			return

		email_exists = any(str(student.email).strip().lower() == email for student in self.system.students)
		if email_exists:
			status.update("A student with that email already exists.")
			return

		new_name = f"{first_name} {last_name}".strip()
		new_password = "temp"
		self.system.addStudent(new_name, email, new_password, hometown)
		created_student = self.system.students[-1] if self.system.students else None
		if created_student is None:
			status.update("Could not create student.")
			return

		self.query_one("#admin-create-first-name", Input).value = ""
		self.query_one("#admin-create-last-name", Input).value = ""
		self.query_one("#admin-create-hometown", Input).value = ""
		self.query_one("#admin-create-email", Input).value = ""
		status.update(
			f"Created student {created_student.name} ({created_student.email}). "
			f"Temporary password: {new_password}. Student can change it later. Save and Exit to persist."
		)

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

		block_message = self._student_request_or_group_block_message()
		if block_message is not None:
			self.student_rows = []
			self.selected_student_ids = []
			self.selected_student_id = None
			self.selected_request_id = None
			self.request_table_mode = None
			self._set_students_view_mode(True)
			table.add_class("hidden")
			requests_table.add_class("hidden")
			interests_table.add_class("hidden")
			self.query_one("#accept-request-button", Button).add_class("hidden")
			self.query_one("#reject-request-button", Button).add_class("hidden")
			self.query_one("#send-request-button", Button).add_class("hidden")
			group_details.update(block_message)
			group_details.remove_class("hidden")
			status.update("You cannot send a new request right now.")
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

	def _student_request_or_group_block_message(self) -> str | None:
		if self.current_student is None or self.db_connection is None or self.system is None:
			return None

		if int(self.current_student.groupID) >= 0:
			return (
				"You already have an active request. "
				"Complete your current request before sending a new one."
			)

		incoming_requests = get_incoming_roommate_requests(
			self.db_connection,
			self.system,
			int(self.current_student.id),
		)
		if any(str(request_row.get("status", "")).lower() == "pending" for request_row in incoming_requests):
			return (
				"You are in a pending request. To send another request, open Respond to Requests "
				"and reject the incoming request first."
			)

		outgoing_requests = get_outgoing_roommate_requests(
			self.db_connection,
			self.system,
			int(self.current_student.id),
		)
		if outgoing_requests:
			return "You already have an active request. Wait for it to finish before sending another one."

		return None

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

		if self.current_student is None or self.system is None:
			group_details.update("No pairings yet.")
			status.update(info_message or "No pairing created yet.")
			group_details.remove_class("hidden")
			return

		current_pairing = self._pairing_for_student(int(self.current_student.id))
		if current_pairing is None:
			group_details.update("No pairing yet. A pairing only appears after everyone accepts the request.")
			status.update(info_message or "No pairing created yet.")
		else:
			group_members = [
				self.system.getStudentById(int(student_id))
				for student_id in current_pairing.get_students()
			]
			group_members = [student for student in group_members if student is not None]
			group_details.update(self._format_assigned_group_status(group_members))
			status.update(info_message or "Pairing status loaded.")

		group_details.remove_class("hidden")

	def _show_request_status_menu(self) -> None:
		status = self.query_one("#menu-status", Label)
		students_table = self.query_one("#students-table", DataTable)
		requests_table = self.query_one("#requests-table", DataTable)
		interests_table = self.query_one("#interests-table", DataTable)
		send_button = self.query_one("#send-request-button", Button)
		accept_button = self.query_one("#accept-request-button", Button)
		reject_button = self.query_one("#reject-request-button", Button)
		group_details = self.query_one("#group-details", Label)

		if self.current_student is None or self.db_connection is None or self.system is None:
			status.update("No logged-in student found.")
			return

		self.request_rows = get_outgoing_roommate_requests(
			self.db_connection,
			self.system,
			int(self.current_student.id),
		)
		self.selected_request_id = None
		self.request_table_mode = "outgoing"

		requests_table.clear(columns=True)
		requests_table.add_columns("Request ID", "Members", "Status")
		for request_row in self.request_rows:
			all_member_ids = [int(request_row["sender_id"]), *[int(member_id) for member_id in request_row["receiver_ids"]]]
			member_names = ", ".join(self._student_name_from_id(member_id) for member_id in all_member_ids)
			requests_table.add_row(
				str(request_row["request_id"]),
				member_names,
				str(request_row["status"]).capitalize(),
			)

		students_table.add_class("hidden")
		interests_table.add_class("hidden")
		send_button.add_class("hidden")
		accept_button.add_class("hidden")
		reject_button.add_class("hidden")
		group_details.add_class("hidden")
		self._set_students_view_mode(True)

		if not self.request_rows:
			status.update("You have no outgoing requests yet.")
		else:
			status.update("Outgoing request statuses loaded.")

		requests_table.remove_class("hidden")
		requests_table.focus()

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

		self.request_rows = get_incoming_roommate_requests(self.db_connection, self.system, int(self.current_student.id))
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
			group_details.add_class("hidden")
		else:
			status.update("Select a request to show response actions.")
			group_details.update("Select a request to view member statuses.")
			group_details.remove_class("hidden")

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

	def _format_assigned_group_status(self, group_members: list[object]) -> str:
		lines = ["Current Pairing"]
		if not group_members:
			lines.append("- No members found for this pairing.")
			return "\n".join(lines)

		lines.append("Members:")
		for member in sorted(group_members, key=lambda student: str(student.name).lower()):
			lines.append(f"- {member.name}")
		return "\n".join(lines)

	def _pairing_for_student(self, student_id: int):
		if self.system is None:
			return None

		for pairing in self.system.pairings:
			if student_id in [int(member_id) for member_id in pairing.get_students()]:
				return pairing
		return None

	def _render_students_table(self) -> None:
		table = self.query_one("#students-table", DataTable)
		table.clear(columns=True)
		table.add_column("Selected", width=10)
		table.add_column("Student ID", width=12)
		table.add_column("Student Name", width=24)
		table.add_column("Interests", width=48)

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
			self.query_one("#view-request-status-button", Button),
			self.query_one("#make-group-button", Button),
			self.query_one("#view-requests-button", Button),
			self.query_one("#change-interests-button", Button),
			self.query_one("#change-password-button", Button),
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
		current_password_label = self.query_one("#change-password-current-label", Label)
		current_password_input = self.query_one("#change-password-current-input", Input)
		new_password_label = self.query_one("#change-password-new-label", Label)
		new_password_input = self.query_one("#change-password-new-input", Input)
		change_password_submit = self.query_one("#change-password-submit-button", Button)
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
		current_password_label.add_class("hidden")
		current_password_input.add_class("hidden")
		new_password_label.add_class("hidden")
		new_password_input.add_class("hidden")
		change_password_submit.add_class("hidden")
		current_password_input.value = ""
		new_password_input.value = ""
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
		success, message = create_roommate_request(self.db_connection, self.system, new_request)
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
		group_details = self.query_one("#group-details", Label)

		if row_index < 0 or row_index >= len(self.request_rows):
			return

		selected_row = self.request_rows[row_index]
		self.selected_request_id = int(selected_row["request_id"])

		request_model = selected_row["request"]
		if isinstance(request_model, roommateRequest):
			sender_id = request_model.getSenderId()
		else:
			sender_id = "Unknown"

		if self.request_table_mode != "incoming":
			accept_button.add_class("hidden")
			reject_button.add_class("hidden")
			status.update(f"Selected request from student {sender_id}. This is a status-only view.")
			if isinstance(request_model, roommateRequest):
				group_details.update(self._format_request_member_statuses(request_model))
				group_details.remove_class("hidden")
			return

		if isinstance(request_model, roommateRequest) and self.current_student is not None:
			current_student_id = int(self.current_student.id)
			student_response = request_model.responses.get(current_student_id)
			if student_response is True:
				accept_button.add_class("hidden")
				reject_button.add_class("hidden")
				status.update(f"Selected request from student {sender_id}. You already accepted this request.")
				return

		accept_button.remove_class("hidden")
		reject_button.remove_class("hidden")
		status.update(f"Selected request from student {sender_id}. Choose Accept or Reject.")

		if isinstance(request_model, roommateRequest):
			group_details.update(self._format_request_member_statuses(request_model))
			group_details.remove_class("hidden")

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
				self.system,
				self.current_student,
				interest_title,
			)
		else:
			success, message = add_interest_to_student(
				self.db_connection,
				self.system,
				self.current_student,
				interest_title,
			)

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

		selected_row = next(
			(row for row in self.request_rows if int(row["request_id"]) == int(self.selected_request_id)),
			None,
		)
		request_model = selected_row["request"] if selected_row is not None else None
		if not isinstance(request_model, roommateRequest):
			status.update("Could not load request details.")
			return

		updated = respond_to_roommate_request(
			self.db_connection,
			self.system,
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

	def _show_change_password_menu(self) -> None:
		status = self.query_one("#menu-status", Label)
		students_table = self.query_one("#students-table", DataTable)
		requests_table = self.query_one("#requests-table", DataTable)
		interests_table = self.query_one("#interests-table", DataTable)
		send_button = self.query_one("#send-request-button", Button)
		accept_button = self.query_one("#accept-request-button", Button)
		reject_button = self.query_one("#reject-request-button", Button)
		group_details = self.query_one("#group-details", Label)
		current_password_label = self.query_one("#change-password-current-label", Label)
		current_password_input = self.query_one("#change-password-current-input", Input)
		new_password_label = self.query_one("#change-password-new-label", Label)
		new_password_input = self.query_one("#change-password-new-input", Input)
		change_password_submit = self.query_one("#change-password-submit-button", Button)

		if self.current_student is None:
			status.update("No logged-in student found.")
			return

		students_table.add_class("hidden")
		requests_table.add_class("hidden")
		interests_table.add_class("hidden")
		send_button.add_class("hidden")
		accept_button.add_class("hidden")
		reject_button.add_class("hidden")
		group_details.add_class("hidden")
		self.request_table_mode = None
		self.selected_request_id = None
		self._set_students_view_mode(True)

		current_password_input.value = ""
		new_password_input.value = ""
		current_password_label.remove_class("hidden")
		current_password_input.remove_class("hidden")
		new_password_label.remove_class("hidden")
		new_password_input.remove_class("hidden")
		change_password_submit.remove_class("hidden")
		status.update("Enter your current password and new password.")
		current_password_input.focus()

	def _submit_change_password(self) -> None:
		status = self.query_one("#menu-status", Label)
		current_password_input = self.query_one("#change-password-current-input", Input)
		new_password_input = self.query_one("#change-password-new-input", Input)

		if self.current_student is None:
			status.update("No logged-in student found.")
			return

		current_password = current_password_input.value
		new_password = new_password_input.value

		if not current_password or not new_password:
			status.update("Please enter both current and new password.")
			return

		if current_password != self.current_student.password:
			status.update("Current password is incorrect.")
			return

		try:
			self.current_student.updatePassword(new_password)
		except ValueError as error:
			status.update(str(error))
			return
		except Exception:
			status.update("Could not update password right now.")
			return

		self._return_to_menu()
		self.query_one("#menu-status", Label).update("Password updated. Save and Exit to persist.")

	def _get_available_interest_titles(self) -> list[str]:
		if self.system is None:
			return []
		return list(self.system.interest_options)

	def _format_request_member_statuses(self, request: roommateRequest) -> str:
		lines = ["Request Member Details:"]
		sender_name = self._student_name_from_id(int(request.getSenderId()))
		sender_interests = self._student_interests_from_id(int(request.getSenderId()))
		lines.append(f"- {sender_name} | Interests: {sender_interests} | Status: Accepted")

		for receiver_id in request.getReceiverIds():
			receiver_id_int = int(receiver_id)
			receiver_name = self._student_name_from_id(receiver_id_int)
			receiver_interests = self._student_interests_from_id(receiver_id_int)
			response = request.responses.get(receiver_id_int)
			member_status = "Pending"
			if response is True:
				member_status = "Accepted"
			elif response is False:
				member_status = "Rejected"
			lines.append(f"- {receiver_name} | Interests: {receiver_interests} | Status: {member_status}")

		return "\n".join(lines)

	def _student_interests_from_id(self, student_id: int) -> str:
		if self.system is None:
			return "No interests"
		student = self.system.getStudentById(student_id)
		if student is None or not student.interests:
			return "No interests"
		return ", ".join(student.interests)

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
		admin_menu = self.query_one("#admin-menu", Container)
		login_status = self.query_one("#status", Label)
		welcome = self.query_one("#menu-welcome", Label)
		email_input = self.query_one("#email", Input)
		password_input = self.query_one("#password", Input)

		if self.db_connection is not None:
			persist_pending_interest_updates(self.db_connection)
			if self.system is not None:
				persist_pending_roommate_requests(self.db_connection, self.system)
				persist_students(self.db_connection, self.system)

		self._return_to_menu()
		self.current_student = None
		self.current_admin = None
		self.current_admin_name = None
		self.group_members = []
		self.student_rows = []
		self.selected_student_ids = []
		self.request_rows = []

		welcome.update("")
		email_input.value = ""
		password_input.value = ""
		admin_menu.add_class("hidden")
		student_menu.add_class("hidden")
		login_panel.remove_class("hidden")
		login_status.update("Logged out.")
		email_input.focus()

	def _save_and_exit(self) -> None:
		if self.db_connection is not None:
			persist_pending_interest_updates(self.db_connection)
			if self.system is not None:
				persist_pending_roommate_requests(self.db_connection, self.system)
				persist_students(self.db_connection, self.system)
		self.exit()


def main() -> None:
	LoginApp().run()


if __name__ == "__main__":
	main()
