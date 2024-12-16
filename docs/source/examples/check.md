# Check example

## Schema example

::::{tab-set}

:::{tab-item} python

```{eval-rst}
.. literalinclude:: ../../../tests/test-docs/test-basic/target/check_schema.py
    :language: python
```

:::

:::{tab-item} sphinx-pandera

```{eval-rst}
.. autopandera_schema:: target.check_schema.Evaluations
```

:::

:::{tab-item} rst

```markdown
.. autopandera_schema:: target.check_schema.Evaluations
```

NB: If you want to use markdown with myst-parser, use the eval-rst directive.

:::

::::

## Model example

::::{tab-set}

:::{tab-item} python

```{eval-rst}
.. literalinclude:: ../../../tests/test-docs/test-basic/target/check_model.py
    :language: python
```

:::

:::{tab-item} sphinx-pandera

```{eval-rst}
.. autopandera_model:: target.check_model.TestModel
```

:::

:::{tab-item} rst

```markdown
.. autopandera_model:: target.check_model.TestModel
```

NB: If you want to use markdown with myst-parser, use the eval-rst directive.

:::

::::
