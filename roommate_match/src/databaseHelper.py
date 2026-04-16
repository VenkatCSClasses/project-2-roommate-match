from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

from .Student import Student
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
	system = create_system_from_database(connection)
	return connection, system


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
