# Basic example

## Pandera Schema

::::{tab-set}

:::{tab-item} python

```{eval-rst}
.. literalinclude:: ../../../tests/test-docs/test-basic/target/basic_schema.py
    :language: python
```

:::

:::{tab-item} sphinx-pandera

```{eval-rst}
.. autopandera_schema:: target.basic_schema.basic_schema
```

:::

:::{tab-item} rst

```markdown
.. autopandera_schema:: target.basic_schema.basic_schema
```

NB: If you want to use markdown with myst-parser, use the eval-rst directive.

:::

::::

## Pandera Model

::::{tab-set}

:::{tab-item} python

```{eval-rst}
.. literalinclude:: ../../../tests/test-docs/test-basic/target/basic_model.py
    :language: python
```

:::

:::{tab-item} sphinx-pandera

```{eval-rst}
.. autopandera_model:: target.basic_model.TestModel
```

:::

:::{tab-item} rst

```markdown
.. autopandera_model:: target.basic_model.TestModel
```

NB: If you want to use markdown with myst-parser, use the eval-rst directive.

:::

::::
