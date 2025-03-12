import dataclasses
import decimal
from collections import defaultdict
from datetime import date, datetime, timedelta
from typing import Any

from warehouse_app.api.schemas import RollRequestCreate, RollStatisticsResponse
from warehouse_app.database.models import RollORM
from warehouse_app.database.repository import RollAbstractReposity


@dataclasses.dataclass(kw_only=True, frozen=True, slots=True)
class RollService:
    roll_repo: RollAbstractReposity

    async def get_rolls(self, filters: dict[str, Any] | None = None) -> list[RollORM]:
        return await self.roll_repo.get_all(filters)

    async def add_roll(self, roll_data: RollRequestCreate) -> RollORM:
        return await self.roll_repo.add(roll_data)

    async def delete_roll(self, roll_id: int) -> RollORM | None:
        return await self.roll_repo.delete(roll_id)

    async def get_statistic(self, date_range: dict[str, list[datetime]]) -> RollStatisticsResponse:
        rolls = await self.roll_repo.get_rolls_in_stock_during_period(date_range)

        if not rolls:
            return RollStatisticsResponse(
                total_added=0,
                total_removed=0,
                avg_length=0,
                avg_weight=0,
                total_weight=0,
                min_max_roll_length={"min_length": 0, "max_length": 0},
                min_max_roll_weight={"min_weight": 0, "max_weight": 0},
                min_max_time_gap={"max_time_gap": 0, "min_time_gap": 0},
                day_min_rolls_count=None,
                day_max_rolls_count=None,
                day_min_weight=None,
                day_max_weight=None,
            )

        total_added_rolls_in_range = [
            roll
            for roll in rolls
            if roll.created_at >= date_range["date_range"][0] and roll.created_at <= date_range["date_range"][1]
        ]
        total_removed_rolls_in_range = [
            roll
            for roll in rolls
            if roll.removed_at is not None
            and roll.removed_at >= date_range["date_range"][0]
            and roll.removed_at <= date_range["date_range"][1]
        ]
        total_rolls_in_range = set(total_added_rolls_in_range + total_removed_rolls_in_range)

        min_max_roll_length, min_max_roll_weight, min_max_time_gap = self._calculate_min_max_periods(
            rolls, total_rolls_in_range
        )

        stock_count: defaultdict[date, int] = defaultdict(int)
        stock_count_weight: defaultdict[date, decimal.Decimal] = defaultdict(decimal.Decimal)

        for roll in total_rolls_in_range:
            stock_count[roll.created_at.date()] += 1
            stock_count_weight[roll.created_at.date()] += decimal.Decimal(roll.weight)
            if roll.removed_at:
                stock_count[roll.removed_at.date()] -= 1

        day_min_rolls_count, day_max_rolls_count = self._get_days_with_min_and_max_period(stock_count)
        day_min_weight, day_max_weight = self._get_days_with_min_and_max_period(stock_count_weight)
        avg_length, avg_weight = self._calculate_avgs(rolls)
        total_added, total_removed, total_weight = self._calculate_totals(
            rolls, total_added_rolls_in_range, total_removed_rolls_in_range
        )

        return RollStatisticsResponse(
            total_added=total_added,
            total_removed=total_removed,
            avg_length=avg_length,
            avg_weight=avg_weight,
            total_weight=total_weight,
            min_max_roll_length=min_max_roll_length,
            min_max_roll_weight=min_max_roll_weight,
            min_max_time_gap=min_max_time_gap,
            day_min_rolls_count=day_min_rolls_count,
            day_max_rolls_count=day_max_rolls_count,
            day_min_weight=day_min_weight,
            day_max_weight=day_max_weight,
        )

    def _get_days_with_min_and_max_period(self, stock_count: dict[date, Any]) -> tuple[date | None, date | None]:
        sorted_dates = sorted(stock_count.keys())

        current_stock = 0
        stock_by_day = {}

        for current_date in sorted_dates:
            current_stock += stock_count[current_date]
            stock_by_day[current_date] = current_stock

        day_min = min(stock_by_day, key=stock_by_day.get, default=None)
        day_max = max(stock_by_day, key=stock_by_day.get, default=None)

        return day_min, day_max

    def _calculate_min_max_periods(
        self, rolls: list[RollORM], total_rolls_in_range: set[RollORM]
    ) -> tuple[dict[str, float], dict[str, float], dict[str, timedelta]]:
        min_max_roll_length = {
            "min_length": min(roll.length for roll in rolls),
            "max_length": max(roll.length for roll in rolls),
        }
        min_max_roll_weight = {
            "min_weight": min(roll.weight for roll in rolls),
            "max_weight": max(roll.weight for roll in rolls),
        }

        min_max_time_gap = {
            "min_time_gap": min(
                [(roll.removed_at - roll.created_at) for roll in total_rolls_in_range if roll.removed_at is not None]
            ),
            "max_time_gap": max(
                [(roll.removed_at - roll.created_at) for roll in total_rolls_in_range if roll.removed_at is not None]
            ),
        }

        return min_max_roll_length, min_max_roll_weight, min_max_time_gap

    def _calculate_totals(
        self,
        rolls: list[RollORM],
        total_added_rolls_in_range: list[RollORM],
        total_removed_rolls_in_range: list[RollORM],
    ) -> tuple[int, int, float]:
        total_added = len(total_added_rolls_in_range)
        total_removed = len(total_removed_rolls_in_range)
        total_weight = sum(roll.weight for roll in rolls)
        return total_added, total_removed, total_weight

    def _calculate_avgs(self, rolls: list[RollORM]) -> tuple[float, float]:
        avg_length = sum(roll.length for roll in rolls) / len(rolls)
        avg_weight = sum(roll.weight for roll in rolls) / len(rolls)
        return avg_length, avg_weight
