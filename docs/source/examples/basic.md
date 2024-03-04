# Basic example

::::{tab-set}

:::{tab-item} python

```{eval-rst}
.. literalinclude:: ../../../tests/test-docs/test-basic/target/basic_model.py
    :language: python
```

:::


:::{tab-item} sphinx-pandera

```{eval-rst}
.. automodule:: target.basic_model
    :members:
    :undoc-members:
```

:::

:::{tab-item} rst



```markdown

.. automodule:: target.basic_model
    :members:
    :undoc-members:  

```

NB: If you want to use markdown with myst-parser, use the eval-rst directive.

:::

::::
