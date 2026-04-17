from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

from .Student import Student
from .roommateRequest import roommateRequest
from .system import RoommateSystem


_PENDING_ROOMMATE_REQUESTS: dict[int, list[roommateRequest]] = {}


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
			group_request_id INTEGER NOT NULL DEFAULT 0,
			sender_id INT NOT NULL,
			receiver_id INT NOT NULL,
			status TEXT NOT NULL DEFAULT 'pending',
			created_at TEXT DEFAULT CURRENT_TIMESTAMP,
			updated_at TEXT DEFAULT CURRENT_TIMESTAMP
		)
		"""
	)
	_request_add_column_if_missing(connection, "roommate_requests", "group_request_id", "INTEGER NOT NULL DEFAULT 0")
	connection.execute(
		"UPDATE roommate_requests SET group_request_id = id WHERE group_request_id = 0"
	)
	connection.commit()


def _request_add_column_if_missing(
	connection: sqlite3.Connection,
	table_name: str,
	column_name: str,
	column_definition: str,
) -> None:
	columns = _table_columns(connection, table_name)
	if column_name in columns:
		return

	connection.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_definition}")


def create_roommate_request(connection: sqlite3.Connection, request: roommateRequest) -> tuple[bool, str]:
	ensure_roommate_requests_table(connection)

	sender_id = int(request.getSenderId())
	receiver_ids = [int(receiver_id) for receiver_id in request.getReceiverIds()]

	if len(receiver_ids) == 0:
		return False, "Select at least one student."

	if len(receiver_ids) > 3:
		return False, "A group request can have at most 3 other students."

	if sender_id in receiver_ids:
		return False, "You cannot send a request to yourself."

	receiver_ids = list(dict.fromkeys(receiver_ids))
	if len(receiver_ids) == 0:
		return False, "Select at least one student."

	group_size = 1 + len(receiver_ids)
	if group_size > 4:
		return False, "A group can have at most 4 people."

	queued_requests = _pending_requests_for_connection(connection)

	active_batch_row = connection.execute(
		"""
		SELECT COUNT(DISTINCT group_request_id)
		FROM roommate_requests
		WHERE sender_id = ? AND status IN ('pending', 'accepted')
		""",
		(sender_id,),
	).fetchone()
	active_batches = int(active_batch_row[0]) if active_batch_row is not None else 0
	active_queued_batches = sum(1 for queued_request in queued_requests if int(queued_request.getSenderId()) == sender_id)
	if active_batches + active_queued_batches >= 1:
		return False, "You already have an active roommate request group."

	current_group_member_ids = _get_sender_group_member_ids(connection, sender_id)
	for queued_request in queued_requests:
		if int(queued_request.getSenderId()) == sender_id:
			current_group_member_ids.update(int(receiver_id) for receiver_id in queued_request.getReceiverIds())
	conflicting_ids = [receiver_id for receiver_id in receiver_ids if receiver_id in current_group_member_ids]
	if conflicting_ids:
		return False, "One or more selected students are already in your active group or pending requests."

	queued_requests.append(roommateRequest(sender_id, receiver_ids[0], *receiver_ids[1:3]))
	return True, "Roommate request queued. Save and Exit to persist."


def persist_pending_roommate_requests(connection: sqlite3.Connection) -> int:
	ensure_roommate_requests_table(connection)
	queued_requests = _pending_requests_for_connection(connection)
	if not queued_requests:
		return 0

	queued_count = len(queued_requests)
	for queued_request in queued_requests:
		sender_id = int(queued_request.getSenderId())
		receiver_ids = [int(receiver_id) for receiver_id in queued_request.getReceiverIds()]
		if not receiver_ids:
			continue

		group_request_id = _next_group_request_id(connection)
		for receiver_id in receiver_ids:
			connection.execute(
				"""
				INSERT INTO roommate_requests (group_request_id, sender_id, receiver_id, status)
				VALUES (?, ?, ?, 'pending')
				""",
				(group_request_id, sender_id, receiver_id),
			)

	connection.commit()
	queued_requests.clear()
	return queued_count


def _pending_requests_for_connection(connection: sqlite3.Connection) -> list[roommateRequest]:
	connection_key = id(connection)
	if connection_key not in _PENDING_ROOMMATE_REQUESTS:
		_PENDING_ROOMMATE_REQUESTS[connection_key] = []
	return _PENDING_ROOMMATE_REQUESTS[connection_key]


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

	group_id_rows = connection.execute(
		"""
		SELECT DISTINCT rr.group_request_id, rr.sender_id
		FROM roommate_requests AS rr
		WHERE rr.receiver_id = ? AND rr.status IN ('pending', 'accepted', 'rejected')
		ORDER BY rr.group_request_id DESC
		""",
		(receiver_id,),
	).fetchall()

	requests: list[dict[str, Any]] = []
	for group_request_id, sender_id in group_id_rows:
		group_rows = _load_request_group_rows(connection, int(group_request_id))
		if not group_rows:
			continue
		requests.append(_request_batch_dict(group_rows))

	return requests


def get_outgoing_roommate_requests(
	connection: sqlite3.Connection,
	sender_id: int,
) -> list[dict[str, Any]]:
	ensure_roommate_requests_table(connection)

	group_id_rows = connection.execute(
		"""
		SELECT DISTINCT rr.group_request_id
		FROM roommate_requests AS rr
		WHERE rr.sender_id = ? AND rr.status IN ('pending', 'accepted')
		ORDER BY rr.group_request_id DESC
		""",
		(sender_id,),
	).fetchall()

	requests: list[dict[str, Any]] = []
	for group_request_id, in group_id_rows:
		group_rows = _load_request_group_rows(connection, int(group_request_id))
		if not group_rows:
			continue
		requests.append(_request_batch_dict(group_rows))

	return requests


def respond_to_roommate_request(
	connection: sqlite3.Connection,
	request_id: int,
	accept: bool,
	responder_id: int | None = None,
) -> bool:
	ensure_roommate_requests_table(connection)
	if responder_id is None:
		return False

	if accept:
		result = connection.execute(
			"""
			UPDATE roommate_requests
			SET status = 'accepted', updated_at = CURRENT_TIMESTAMP
			WHERE group_request_id = ? AND receiver_id = ? AND status = 'pending'
			""",
			(request_id, responder_id),
		)
	else:
		result = connection.execute(
			"""
			UPDATE roommate_requests
			SET status = 'rejected', updated_at = CURRENT_TIMESTAMP
			WHERE group_request_id = ? AND status IN ('pending', 'accepted')
			""",
			(request_id,),
		)
	connection.commit()
	return result.rowcount > 0


def get_group_status_for_student(
	connection: sqlite3.Connection,
	student_id: int,
) -> list[dict[str, str]]:
	ensure_roommate_requests_table(connection)

	group_id_rows = connection.execute(
		"""
		SELECT DISTINCT rr.group_request_id
		FROM roommate_requests AS rr
		WHERE (rr.sender_id = ? OR rr.receiver_id = ?) AND rr.status IN ('pending', 'accepted')
		ORDER BY rr.group_request_id DESC
		""",
		(student_id, student_id),
	).fetchall()

	members: dict[str, dict[str, str]] = {}
	for group_request_id, in group_id_rows:
		group_rows = _load_request_group_rows(connection, int(group_request_id))
		if not group_rows:
			continue
		for _, _, sender_id, receiver_id, status in group_rows:
			sender_key = str(sender_id)
			receiver_key = str(receiver_id)

			if sender_key not in members:
				members[sender_key] = {"id": sender_key, "status": "Accepted"}

			receiver_status = "Pending"
			if status == "accepted":
				receiver_status = "Accepted"
			elif status == "rejected":
				receiver_status = "Rejected"

			if receiver_key not in members:
				members[receiver_key] = {"id": receiver_key, "status": receiver_status}
			elif members[receiver_key]["status"] != "Accepted":
				members[receiver_key]["status"] = receiver_status

	return list(members.values())


def revoke_outgoing_roommate_requests(connection: sqlite3.Connection, sender_id: int) -> int:
	ensure_roommate_requests_table(connection)
	result = connection.execute(
		"""
		UPDATE roommate_requests
		SET status = 'revoked', updated_at = CURRENT_TIMESTAMP
		WHERE sender_id = ? AND status IN ('pending', 'accepted')
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
		WHERE group_request_id = ? AND sender_id = ? AND status IN ('pending', 'accepted')
		""",
		(request_id, sender_id),
	)
	connection.commit()
	return result.rowcount > 0


def back_out_of_roommate_group(connection: sqlite3.Connection, student_id: int) -> int:
	ensure_roommate_requests_table(connection)

	accepted_links = connection.execute(
		"""
		SELECT group_request_id, sender_id, receiver_id
		FROM roommate_requests
		WHERE status = 'accepted' AND (sender_id = ? OR receiver_id = ?)
		""",
		(student_id, student_id),
	).fetchall()

	other_member_ids: set[int] = set()
	for _, sender_id, receiver_id in accepted_links:
		if int(sender_id) == student_id and int(receiver_id) != student_id:
			other_member_ids.add(int(receiver_id))
		elif int(receiver_id) == student_id and int(sender_id) != student_id:
			other_member_ids.add(int(sender_id))

	result = connection.execute(
		"""
		UPDATE roommate_requests
		SET status = 'withdrawn', updated_at = CURRENT_TIMESTAMP
		WHERE status IN ('accepted', 'pending') AND (sender_id = ? OR receiver_id = ?)
		""",
		(student_id, student_id),
	)

	remaining_members = sorted(other_member_ids)
	for index, left_member in enumerate(remaining_members):
		for right_member in remaining_members[index + 1 :]:
			_ensure_accepted_link_between(connection, left_member, right_member)

	connection.commit()
	return int(result.rowcount)


def _next_group_request_id(connection: sqlite3.Connection) -> int:
	row = connection.execute("SELECT COALESCE(MAX(group_request_id), 0) + 1 FROM roommate_requests").fetchone()
	return int(row[0]) if row is not None else 1


def _load_request_group_rows(
	connection: sqlite3.Connection,
	group_request_id: int,
) -> list[tuple[int, int, int, int, str]]:
	rows = connection.execute(
		"""
		SELECT group_request_id, id, sender_id, receiver_id, status
		FROM roommate_requests
		WHERE group_request_id = ?
		ORDER BY created_at DESC, id DESC
		""",
		(group_request_id,),
	).fetchall()
	return [
		(int(row[0]), int(row[1]), int(row[2]), int(row[3]), str(row[4]))
		for row in rows
	]


def _request_batch_status(group_rows: list[tuple[int, int, int, int, str]]) -> str:
	statuses = [str(row[4]) for row in group_rows]
	if any(status == "rejected" for status in statuses):
		return "rejected"
	if all(status == "accepted" for status in statuses):
		return "accepted"
	if any(status == "pending" for status in statuses):
		return "pending"
	return statuses[0] if statuses else "pending"


def _group_roommate_request_rows(
	rows: list[tuple[int, int, int, int, str]]
) -> dict[int, list[tuple[int, int, int, int, str]]]:
	grouped_rows: dict[int, list[tuple[int, int, int, int, str]]] = {}
	for row in rows:
		group_request_id = int(row[0])
		grouped_rows.setdefault(group_request_id, []).append(row)
	return grouped_rows


def _request_for_group_rows(group_rows: list[tuple[int, int, int, int, str]]) -> roommateRequest:
	sender_id = int(group_rows[0][2])
	receiver_ids = [int(row[3]) for row in group_rows]
	request = roommateRequest(sender_id, receiver_ids[0], *receiver_ids[1:3])
	for _, _, _, receiver_id, status in group_rows:
		if status == "accepted":
			request.accept_request(int(receiver_id))
		elif status == "rejected":
			request.reject_request(int(receiver_id))
	request.updateStatus()
	return request


def _request_batch_dict(group_rows: list[tuple[int, int, int, int, str]]) -> dict[str, Any]:
	return {
		"request_id": int(group_rows[0][0]),
		"sender_id": int(group_rows[0][2]),
		"receiver_ids": [int(row[3]) for row in group_rows],
		"status": _request_batch_status(group_rows),
		"request": _request_for_group_rows(group_rows),
	}


def _ensure_accepted_link_between(connection: sqlite3.Connection, student_a: int, student_b: int) -> None:
	existing = connection.execute(
		"""
		SELECT id, status
		FROM roommate_requests
		WHERE
			((sender_id = ? AND receiver_id = ?) OR (sender_id = ? AND receiver_id = ?))
			AND status IN ('pending', 'accepted')
		LIMIT 1
		""",
		(student_a, student_b, student_b, student_a),
	).fetchone()

	if existing is not None:
		if str(existing[1]) == 'pending':
			connection.execute(
				"""
				UPDATE roommate_requests
				SET status = 'accepted', updated_at = CURRENT_TIMESTAMP
				WHERE id = ?
				""",
				(int(existing[0]),),
			)
		return

	connection.execute(
		"""
		INSERT INTO roommate_requests (sender_id, receiver_id, status)
		VALUES (?, ?, 'accepted')
		""",
		(student_a, student_b),
	)


def get_interest_options(connection: sqlite3.Connection) -> list[tuple[int, str]]:
	if not _table_exists(connection, "interests"):
		return []

	rows = connection.execute("SELECT id, title FROM interests ORDER BY title").fetchall()
	return [
		(int(row[0]), str(row[1]))
		for row in rows
		if row
		and row[0] is not None
		and row[1] is not None
		and str(row[1]).strip().lower() not in {"title", "interest"}
	]


def get_student_interest_titles(connection: sqlite3.Connection, student_id: int) -> list[str]:
	return _get_student_interest_titles(connection, student_id)


def add_interest_to_student(
	connection: sqlite3.Connection,
	student_id: int,
	interest_title: str,
) -> tuple[bool, str]:
	join_table = _get_interest_join_table(connection)
	interest_id = _find_interest_id(connection, interest_title)
	if interest_id is None:
		return False, "That interest does not exist."

	existing = connection.execute(
		f"SELECT 1 FROM {join_table} WHERE student_id = ? AND interest_id = ? LIMIT 1",
		(student_id, interest_id),
	).fetchone()
	if existing is not None:
		return False, "Interest already exists in your profile."

	columns = _table_columns(connection, join_table)
	if "id" in columns:
		next_id_row = connection.execute(f"SELECT COALESCE(MAX(id), 0) + 1 FROM {join_table}").fetchone()
		next_id = int(next_id_row[0]) if next_id_row is not None else 1
		connection.execute(
			f"INSERT INTO {join_table} (id, student_id, interest_id) VALUES (?, ?, ?)",
			(next_id, student_id, interest_id),
		)
	else:
		connection.execute(
			f"INSERT INTO {join_table} (student_id, interest_id) VALUES (?, ?)",
			(student_id, interest_id),
		)

	connection.commit()
	return True, "Interest added."


def remove_interest_from_student(
	connection: sqlite3.Connection,
	student_id: int,
	interest_title: str,
) -> tuple[bool, str]:
	join_table = _get_interest_join_table(connection)
	interest_id = _find_interest_id(connection, interest_title)
	if interest_id is None:
		return False, "That interest does not exist."

	result = connection.execute(
		f"DELETE FROM {join_table} WHERE student_id = ? AND interest_id = ?",
		(student_id, interest_id),
	)
	connection.commit()

	if result.rowcount == 0:
		return False, "Interest was not in your profile."
	return True, "Interest removed."


def _get_interest_join_table(connection: sqlite3.Connection) -> str:
	join_table = _choose_interest_join_table(connection)
	if join_table is None:
		raise ValueError("Interests join table not found. Expected students_to_interests or students_to_interest.")
	return join_table


def _find_interest_id(connection: sqlite3.Connection, interest_title: str) -> int | None:
	if not _table_exists(connection, "interests"):
		return None

	row = connection.execute(
		"SELECT id FROM interests WHERE LOWER(title) = LOWER(?) LIMIT 1",
		(interest_title,),
	).fetchone()
	if row is None:
		return None
	return int(row[0])


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
