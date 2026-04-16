from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

from .Student import Student
from .roommateRequest import roommateRequest
from .system import RoommateSystem


def get_default_database_path() -> Path:
	return Path(__file__).resolve().parents[2] / "app.db"


def connect_database(database_path: str | Path | None = None) -> sqlite3.Connection:
	path = Path(database_path) if database_path is not None else get_default_database_path()
	return sqlite3.connect(path)


def create_system_from_database(connection: sqlite3.Connection) -> RoommateSystem:
	system = RoommateSystem()
	_populate_students(connection, system)
	_populate_interest_options(connection, system)
	_populate_preference_options(connection, system)
	return system


def bootstrap_database_and_system(
	database_path: str | Path | None = None,
) -> tuple[sqlite3.Connection, RoommateSystem]:
	connection = connect_database(database_path)
	ensure_roommate_requests_table(connection)
	system = create_system_from_database(connection)
	return connection, system


def ensure_roommate_requests_table(connection: sqlite3.Connection) -> None:
	connection.execute(
		"""
		CREATE TABLE IF NOT EXISTS roommate_requests (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			sender_id INT NOT NULL,
			receiver_id INT NOT NULL,
			status TEXT NOT NULL DEFAULT 'pending',
			created_at TEXT DEFAULT CURRENT_TIMESTAMP,
			updated_at TEXT DEFAULT CURRENT_TIMESTAMP
		)
		"""
	)
	connection.commit()


def create_roommate_request(connection: sqlite3.Connection, request: roommateRequest) -> tuple[bool, str]:
	ensure_roommate_requests_table(connection)

	sender_id = int(request.getSenderId())
	receiver_id = int(request.getReceiver1Id())

	if sender_id == receiver_id:
		return False, "You cannot send a request to yourself."

	outgoing_count_row = connection.execute(
		"""
		SELECT COUNT(*)
		FROM roommate_requests
		WHERE sender_id = ? AND status IN ('pending', 'accepted')
		""",
		(sender_id,),
	).fetchone()
	outgoing_count = int(outgoing_count_row[0]) if outgoing_count_row is not None else 0
	if outgoing_count >= 10:
		return False, "You cannot send more than 10 outgoing roommate requests."

	current_group_member_ids = _get_sender_group_member_ids(connection, sender_id)
	if len(current_group_member_ids) >= 4 and receiver_id not in current_group_member_ids:
		return False, "Group is full. A group can have at most 4 people."

	if receiver_id in current_group_member_ids:
		return False, "This student is already in your group or pending group requests."

	existing = connection.execute(
		"""
		SELECT id
		FROM roommate_requests
		WHERE sender_id = ? AND receiver_id = ? AND status = 'pending'
		""",
		(sender_id, receiver_id),
	).fetchone()

	if existing is not None:
		return False, "A pending request already exists for this student."

	connection.execute(
		"""
		INSERT INTO roommate_requests (sender_id, receiver_id, status)
		VALUES (?, ?, 'pending')
		""",
		(sender_id, receiver_id),
	)
	connection.commit()
	return True, "Roommate request sent."


def _get_sender_group_member_ids(connection: sqlite3.Connection, sender_id: int) -> set[int]:
	rows = connection.execute(
		"""
		SELECT receiver_id
		FROM roommate_requests
		WHERE sender_id = ? AND status IN ('pending', 'accepted')
		""",
		(sender_id,),
	).fetchall()

	member_ids = {sender_id}
	member_ids.update(int(row[0]) for row in rows)
	return member_ids


def get_incoming_roommate_requests(
	connection: sqlite3.Connection,
	receiver_id: int,
) -> list[dict[str, Any]]:
	ensure_roommate_requests_table(connection)

	rows = connection.execute(
		"""
		SELECT rr.id, rr.sender_id, rr.receiver_id, rr.status, s.name
		FROM roommate_requests AS rr
		LEFT JOIN students AS s ON s.id = rr.sender_id
		WHERE rr.receiver_id = ? AND rr.status IN ('pending', 'accepted', 'rejected')
		ORDER BY rr.created_at DESC, rr.id DESC
		""",
		(receiver_id,),
	).fetchall()

	requests: list[dict[str, Any]] = []
	for request_id, sender_id, request_receiver_id, status, sender_name in rows:
		request_model = roommateRequest(sender_id, request_receiver_id)
		if status == "accepted":
			request_model.accept_request()
		elif status == "rejected":
			request_model.reject_request()

		requests.append(
			{
				"request_id": int(request_id),
				"sender_name": str(sender_name) if sender_name is not None else f"Student {sender_id}",
				"status": str(status),
				"request": request_model,
			}
		)

	return requests


def get_outgoing_roommate_requests(
	connection: sqlite3.Connection,
	sender_id: int,
) -> list[dict[str, Any]]:
	ensure_roommate_requests_table(connection)

	rows = connection.execute(
		"""
		SELECT rr.id, rr.sender_id, rr.receiver_id, rr.status, s.name
		FROM roommate_requests AS rr
		LEFT JOIN students AS s ON s.id = rr.receiver_id
		WHERE rr.sender_id = ? AND rr.status = 'pending'
		ORDER BY rr.created_at DESC, rr.id DESC
		""",
		(sender_id,),
	).fetchall()

	requests: list[dict[str, Any]] = []
	for request_id, request_sender_id, receiver_id, status, receiver_name in rows:
		request_model = roommateRequest(request_sender_id, receiver_id)
		requests.append(
			{
				"request_id": int(request_id),
				"receiver_name": str(receiver_name) if receiver_name is not None else f"Student {receiver_id}",
				"status": str(status),
				"request": request_model,
			}
		)

	return requests


def respond_to_roommate_request(
	connection: sqlite3.Connection,
	request_id: int,
	accept: bool,
) -> bool:
	ensure_roommate_requests_table(connection)
	status = "accepted" if accept else "rejected"
	result = connection.execute(
		"""
		UPDATE roommate_requests
		SET status = ?, updated_at = CURRENT_TIMESTAMP
		WHERE id = ?
		""",
		(status, request_id),
	)
	connection.commit()
	return result.rowcount > 0


def get_group_status_for_student(
	connection: sqlite3.Connection,
	student_id: int,
) -> list[dict[str, str]]:
	ensure_roommate_requests_table(connection)

	rows = connection.execute(
		"""
		SELECT rr.sender_id, rr.receiver_id, rr.status, sender.name, receiver.name
		FROM roommate_requests AS rr
		LEFT JOIN students AS sender ON sender.id = rr.sender_id
		LEFT JOIN students AS receiver ON receiver.id = rr.receiver_id
		WHERE (rr.sender_id = ? OR rr.receiver_id = ?) AND rr.status IN ('pending', 'accepted')
		ORDER BY rr.created_at DESC, rr.id DESC
		""",
		(student_id, student_id),
	).fetchall()

	members: dict[str, dict[str, str]] = {}
	for sender_id, receiver_id, status, sender_name, receiver_name in rows:
		sender_key = str(sender_id)
		receiver_key = str(receiver_id)

		if sender_key not in members:
			members[sender_key] = {
				"id": sender_key,
				"name": str(sender_name) if sender_name is not None else f"Student {sender_id}",
				"status": "Accepted",
			}

		receiver_status = "Pending"
		if status == "accepted":
			receiver_status = "Accepted"
		elif status == "rejected":
			receiver_status = "Rejected"

		if receiver_key not in members:
			members[receiver_key] = {
				"id": receiver_key,
				"name": str(receiver_name) if receiver_name is not None else f"Student {receiver_id}",
				"status": receiver_status,
			}
		elif members[receiver_key]["status"] != "Accepted":
			members[receiver_key]["status"] = receiver_status

	return list(members.values())


def revoke_outgoing_roommate_requests(connection: sqlite3.Connection, sender_id: int) -> int:
	ensure_roommate_requests_table(connection)
	result = connection.execute(
		"""
		UPDATE roommate_requests
		SET status = 'revoked', updated_at = CURRENT_TIMESTAMP
		WHERE sender_id = ? AND status = 'pending'
		""",
		(sender_id,),
	)
	connection.commit()
	return int(result.rowcount)


def revoke_specific_outgoing_roommate_request(
	connection: sqlite3.Connection,
	sender_id: int,
	request_id: int,
) -> bool:
	ensure_roommate_requests_table(connection)
	result = connection.execute(
		"""
		UPDATE roommate_requests
		SET status = 'revoked', updated_at = CURRENT_TIMESTAMP
		WHERE id = ? AND sender_id = ? AND status = 'pending'
		""",
		(request_id, sender_id),
	)
	connection.commit()
	return result.rowcount > 0


def back_out_of_roommate_group(connection: sqlite3.Connection, student_id: int) -> int:
	ensure_roommate_requests_table(connection)
	result = connection.execute(
		"""
		UPDATE roommate_requests
		SET status = 'withdrawn', updated_at = CURRENT_TIMESTAMP
		WHERE status = 'accepted' AND (sender_id = ? OR receiver_id = ?)
		""",
		(student_id, student_id),
	)
	connection.commit()
	return int(result.rowcount)


def _table_exists(connection: sqlite3.Connection, table_name: str) -> bool:
	row = connection.execute(
		"SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?",
		(table_name,),
	).fetchone()
	return row is not None


def _table_columns(connection: sqlite3.Connection, table_name: str) -> set[str]:
	rows = connection.execute(f"PRAGMA table_info({table_name})").fetchall()
	return {str(row[1]) for row in rows}


def _choose_interest_join_table(connection: sqlite3.Connection) -> str | None:
	if _table_exists(connection, "students_to_interests"):
		return "students_to_interests"
	if _table_exists(connection, "students_to_interest"):
		return "students_to_interest"
	return None


def _get_existing_groups(connection: sqlite3.Connection) -> dict[int, int]:
	groups: dict[int, int] = {}

	if _table_exists(connection, "students"):
		student_columns = _table_columns(connection, "students")
		if "group_id" in student_columns:
			rows = connection.execute(
				"SELECT id, group_id FROM students WHERE group_id IS NOT NULL"
			).fetchall()
			groups.update({int(student_id): int(group_id) for student_id, group_id in rows})

	if _table_exists(connection, "students_to_groups"):
		rows = connection.execute(
			"SELECT student_id, group_id FROM students_to_groups"
		).fetchall()
		groups.update({int(student_id): int(group_id) for student_id, group_id in rows})

	return groups


def _populate_students(connection: sqlite3.Connection, system: RoommateSystem) -> None:
	if not _table_exists(connection, "students"):
		return

	rows = connection.execute(
		"SELECT id, name, email, password, hometown FROM students"
	).fetchall()
	groups_by_student = _get_existing_groups(connection)

	for row in rows:
		if _looks_like_header_row(row):
			continue

		student_id = int(row[0])
		student = Student(
			student_id,
			str(row[1]),
			str(row[2]),
			str(row[3]),
			str(row[4]),
		)
		student.groupID = groups_by_student.get(student_id, -1)
		student.interests = _get_student_interest_titles(connection, student_id)
		student.preferences = _get_student_preferences(connection, student_id)
		system.students.append(student)


def _looks_like_header_row(row: tuple[Any, ...]) -> bool:
	id_value = str(row[0]).strip().lower()
	name_value = str(row[1]).strip().lower()
	return id_value in {"id", "student_id"} or name_value in {"name", "student_name"}


def _get_student_interest_titles(connection: sqlite3.Connection, student_id: int) -> list[str]:
	join_table = _choose_interest_join_table(connection)
	if join_table is None or not _table_exists(connection, "interests"):
		return []

	rows = connection.execute(
		f"""
		SELECT i.title
		FROM {join_table} AS sti
		JOIN interests AS i ON i.id = sti.interest_id
		WHERE sti.student_id = ?
		ORDER BY i.title
		""",
		(student_id,),
	).fetchall()
	return [str(row[0]) for row in rows if row and row[0] is not None]


def _get_student_preferences(connection: sqlite3.Connection, student_id: int) -> list[str]:
	if not _table_exists(connection, "student_preferences"):
		return []

	rows = connection.execute(
		"""
		SELECT preference
		FROM student_preferences
		WHERE student_id = ?
		ORDER BY preference
		""",
		(student_id,),
	).fetchall()
	return [str(row[0]) for row in rows if row and row[0] is not None]


def _populate_interest_options(connection: sqlite3.Connection, system: RoommateSystem) -> None:
	if not _table_exists(connection, "interests"):
		return

	rows = connection.execute("SELECT title FROM interests ORDER BY title").fetchall()
	system.interest_options = [
		str(row[0])
		for row in rows
		if row and row[0] is not None and str(row[0]).strip().lower() not in {"title", "interest"}
	]


def _populate_preference_options(connection: sqlite3.Connection, system: RoommateSystem) -> None:
	if not _table_exists(connection, "preference_options"):
		return

	rows = connection.execute("SELECT preference FROM preference_options ORDER BY preference").fetchall()
	system.preference_options = [
		str(row[0])
		for row in rows
		if row and row[0] is not None and str(row[0]).strip().lower() != "preference"
	]
