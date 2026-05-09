from datetime import datetime
from pathlib import Path
import sqlite3

from app.schemas.ticket import (
    Ticket,
    TicketCategory,
    TicketCreate,
    TicketPriority,
    TicketStats,
    TicketStatus,
    TicketUpdate,
)


class TicketNotFoundError(ValueError):
    pass


class TicketStore:
    def __init__(self, db_path: str | Path) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def create_ticket(self, payload: TicketCreate) -> Ticket:
        now = self._now()
        ticket_id = self._next_ticket_id(now)
        with self._connect() as connection:
            connection.execute(
                """
                insert into tickets (
                    id, title, description, category, priority, status, ai_summary,
                    suggested_resolution, source_question, created_at, updated_at, resolution_note
                )
                values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    ticket_id,
                    payload.title,
                    payload.description,
                    payload.category.value,
                    payload.priority.value,
                    TicketStatus.OPEN.value,
                    payload.ai_summary,
                    payload.suggested_resolution,
                    payload.source_question,
                    now.isoformat(),
                    now.isoformat(),
                    "",
                ),
            )
        return self.get_ticket(ticket_id)

    def get_ticket(self, ticket_id: str) -> Ticket:
        with self._connect() as connection:
            row = connection.execute(
                "select * from tickets where id = ?",
                (ticket_id,),
            ).fetchone()
        if row is None:
            raise TicketNotFoundError(f"Ticket not found: {ticket_id}")
        return self._row_to_ticket(row)

    def list_tickets(
        self,
        *,
        status: TicketStatus | None = None,
        category: TicketCategory | None = None,
        priority: TicketPriority | None = None,
    ) -> list[Ticket]:
        clauses: list[str] = []
        params: list[str] = []
        if status is not None:
            clauses.append("status = ?")
            params.append(status.value)
        if category is not None:
            clauses.append("category = ?")
            params.append(category.value)
        if priority is not None:
            clauses.append("priority = ?")
            params.append(priority.value)

        sql = "select * from tickets"
        if clauses:
            sql += " where " + " and ".join(clauses)
        sql += " order by created_at desc, id desc"

        with self._connect() as connection:
            rows = connection.execute(sql, params).fetchall()
        return [self._row_to_ticket(row) for row in rows]

    def update_ticket(self, ticket_id: str, payload: TicketUpdate) -> Ticket:
        self.get_ticket(ticket_id)
        updates: list[str] = []
        params: list[str] = []
        if payload.status is not None:
            updates.append("status = ?")
            params.append(payload.status.value)
        if payload.priority is not None:
            updates.append("priority = ?")
            params.append(payload.priority.value)
        if payload.resolution_note is not None:
            updates.append("resolution_note = ?")
            params.append(payload.resolution_note)

        updates.append("updated_at = ?")
        params.append(self._now().isoformat())
        params.append(ticket_id)

        with self._connect() as connection:
            connection.execute(
                f"update tickets set {', '.join(updates)} where id = ?",
                params,
            )
        return self.get_ticket(ticket_id)

    def get_stats(self) -> TicketStats:
        with self._connect() as connection:
            total = connection.execute("select count(*) from tickets").fetchone()[0]
            by_status = self._count_by(connection, "status")
            by_category = self._count_by(connection, "category")
            by_priority = self._count_by(connection, "priority")

        return TicketStats(
            total=total,
            by_status=by_status,
            by_category=by_category,
            by_priority=by_priority,
        )

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                create table if not exists tickets (
                    id text primary key,
                    title text not null,
                    description text not null,
                    category text not null,
                    priority text not null,
                    status text not null,
                    ai_summary text not null,
                    suggested_resolution text not null,
                    source_question text not null,
                    created_at text not null,
                    updated_at text not null,
                    resolution_note text not null
                )
                """
            )

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _next_ticket_id(self, now: datetime) -> str:
        prefix = f"TICKET-{now:%Y%m%d}"
        with self._connect() as connection:
            count = connection.execute(
                "select count(*) from tickets where id like ?",
                (f"{prefix}-%",),
            ).fetchone()[0]
        return f"{prefix}-{count + 1:04d}"

    @staticmethod
    def _now() -> datetime:
        return datetime.now()

    @staticmethod
    def _row_to_ticket(row: sqlite3.Row) -> Ticket:
        return Ticket(
            id=row["id"],
            title=row["title"],
            description=row["description"],
            category=row["category"],
            priority=row["priority"],
            status=row["status"],
            ai_summary=row["ai_summary"],
            suggested_resolution=row["suggested_resolution"],
            source_question=row["source_question"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
            resolution_note=row["resolution_note"],
        )

    @staticmethod
    def _count_by(connection: sqlite3.Connection, column: str) -> dict[str, int]:
        rows = connection.execute(
            f"select {column}, count(*) as count from tickets group by {column}"
        ).fetchall()
        return {row[0]: row[1] for row in rows}
