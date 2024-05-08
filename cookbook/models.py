from __future__ import annotations

import json
from abc import ABC, abstractmethod
from pydantic import BaseModel


class Stack(BaseModel):
    quantity: int
    item: str


class Recipe(BaseModel):
    name: str
    inputs: list[Stack]
    outputs: list[Stack]
    time: int

    def input_items(self) -> list[str]:
        return [stack.item for stack in self.inputs]

    def output_items(self) -> list[str]:
        return [stack.item for stack in self.outputs]


class RecipeBook(BaseModel):
    name: str
    recipes: list[Recipe]

    @staticmethod
    def load(path: str) -> RecipeBook:
        """
        Load a recipe book from a path.
        """
        with open(path, "r") as f:
            data = json.loads(f.read())
            return RecipeBook(**data)

    def dump(self, path: str) -> None:
        with open(path, "w+") as f:
            f.write(self.json())


class Flow(BaseModel):
    item: str
    rate: float

    def __mul__(self, other: float) -> Flow:
        return Flow(item=self.item, rate=self.rate * other)

    def __rmul__(self, other: float) -> Flow:
        return self.__mul__(other)

    def __div__(self, other: float) -> Flow:
        return Flow(item=self.item, rate=self.rate / other)

    def __rdiv__(self, other: float) -> Flow:
        return Flow(item=self.item, rate=other / self.rate)

class Runnable(ABC):
    @abstractmethod
    def run(self, *flows: Flow) -> list[Flow]:
        ...

class Assembler(BaseModel, Runnable):
    """
    Runnable object that executes a recipe.
    """
    
    recipe: Recipe

    def fill_rate_by_item(self, *flows: Flow) -> dict[str, float]:
        """
        Compute the rate at which each item in the recipe is provided by the input flow.
        """
        fill_rates: dict[str, float] = {}
        for stack in self.recipe.inputs:
            fill_rates[stack.item] = 0.0
            for flow in flows:
                if flow.item == stack.item:
                    fill_rates[stack.item] += flow.rate

        return fill_rates

    def fill_time(self, *flows: Flow) -> float:
        """
        Compute the time it takes to fully provide all inputs to the recipe.
        """
        fill_rates = self.fill_rate_by_item(*flows)

        fill_times: list[float] = []
        for stack in self.recipe.inputs:
            fill_time = stack.quantity / fill_rates[stack.item]
            fill_times.append(fill_time)

        return max(fill_times)

    def run(self, *flows: Flow) -> list[Flow]:
        run_time = max(self.fill_time(*flows), self.recipe.time)

        output: list[Flow] = []
        for stack in self.recipe.outputs:
            output_flow = Flow(item=stack.item, rate=(stack.quantity / run_time))
            output.append(output_flow)

        return output

class InfiniteProvider(BaseModel, Runnable):
    """
    Runnable object that provides an infinite amount of an item.
    """
    
    item: str

    def run(self, *flows: Flow) -> list[Flow]:
        return Flow(item=self.item, rate=float("INF"))

