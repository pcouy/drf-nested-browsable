:warning: Work In Progress :warning:

# Writable Nested Serializers with Browsable API Forms

This plugin is intended to provide writable nested serializers (similar to [the recommended plugin from DRF documentation](https://github.com/beda-software/drf-nested-browsable.git)) that bring their own forms for the Browsable API renderer.

## Try it out

This project's dependencies are managed using [`poetry`](https://python-poetry.org/)

```bash
git clone https://github.com/pcouy/drf-nested-browsable
cd drf-nested-browsable
poetry install
cd example
poetry shell
python manage.py migrate
python manage.py runserver
```

The above commands will install the dependencies, run the DB migrations, and launch a development server of the example project that uses the provided serializers.

## Current state of the project

### Done

* Ability to write to a reverse `ForeignKey` relationship using serializer `Meta` class
* Dynamic form for `WritableNestedListSerializer` that allows adding and removing children from the Browsable API
* Arbitrary nesting depth
* Dynamically removing the parent field from serializers when used as an inner serializer
* Basic example

### To do

* Write documentation / Auto-generate it from the docstrings ([pdoc](https://pdoc.dev/) ?)
* Write tests/specs (from example ?)
* Better form design
* Add `ManyToMany` to example (and test it)
* Consider database schema constrains :
  * Look into what `drf-writable-nested` does with uniqueness
  * When the foreign key can be `null`, show a multiple select field for attaching orphan instances to a parent instance
  * Show a multiple select field for `ManyToMany` relationships
