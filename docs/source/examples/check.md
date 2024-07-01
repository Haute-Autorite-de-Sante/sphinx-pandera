# Check example

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
.. automodule:: target.check_model
:members:
:undoc-members:
```

NB: If you want to use markdown with myst-parser, use the eval-rst directive.

:::

::::
