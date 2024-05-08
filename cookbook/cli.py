from __future__ import annotations

from r.models import Stack, Recipe, RecipeBook

import click
import rich
import os

APP_NAME = "recipe"


@click.group()
@click.pass_context
def cli(context: click.Context) -> None:
    context.ensure_object(dict)


@cli.group()
@click.option("--book", type=str, default="recipe", help="Name of the book to manage.")
@click.pass_context
def recipe(context: click.Context, book: str) -> None:
    """
    Manage recipes in a recipe book.
    """
    path = os.path.join(click.get_app_dir(APP_NAME), f"{book}.book")
    context.obj["RECIPE_BOOK_PATH"] = path

    try:
        context.obj["RECIPE_BOOK"] = RecipeBook.load(path)
    except FileNotFoundError:
        context.obj["RECIPE_BOOK"] = RecipeBook(name=book, recipes=[])

    @context.call_on_close
    def write_recipe_book() -> None:
        context.obj["RECIPE_BOOK"].dump(context.obj["RECIPE_BOOK_PATH"])


@recipe.command()
@click.option("--name", "-n", type=str, help="A helpful description for the recipe.")
@click.option(
    "--input", "-i", multiple=True, type=(int, str), help="An input to the recipe."
)
@click.option(
    "--output", "-o", multiple=True, type=(int, str), help="An output of the recipe."
)
@click.option(
    "--time", "-t", type=int, help="Time (in seconds) the recipe takes to execute."
)
@click.pass_context
def add(
    context: click.Context,
    name: str,
    input: list[tuple[int, str]],
    output: list[tuple[int, str]],
    time: int,
) -> None:
    """
    Add a recipe to the book.
    """
    recipe = Recipe(
        name=name,
        inputs=[Stack(quantity=stack[0], item=stack[1]) for stack in input],
        outputs=[Stack(quantity=stack[0], item=stack[1]) for stack in output],
        time=time,
    )
    context.obj["RECIPE_BOOK"].recipes.append(recipe)


@recipe.command()
@click.pass_context
def list(context: click.Context) -> None:
    """
    List all recipes in the book.
    """
    for recipe in context.obj["RECIPE_BOOK"]:
        rich.print(recipe)


@recipe.command()
@click.option("--input", "-i", type=str, multiple=True)
@click.option("--output", "-o", type=str, multiple=True)
@click.pass_context
def search(context: click.Context, input: list[str], output: list[str]) -> None:
    """
    Search all recipes by their inputs and outputs.
    """
    for recipe in context.obj["RECIPE_BOOK"].recipes:
        matches, total = 0, len(input + output)
        for input_item in input:
            if input_item in recipe.input_items():
                matches += 1

        for output_item in output:
            if output_item in recipe.output_items():
                matches += 1

        if matches == total:
            rich.print(recipe)


if __name__ == "__main__":
    cli(obj={})
