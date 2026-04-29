
.. py:module:: target.check_schema


.. py:class:: LiteralBool()
   :module: target.check_schema


   .. py:method:: LiteralBool.coerce(series: ~pandas.core.series.Series) -> ~pandas.core.series.Series
      :module: target.check_schema

      Coerce a pandas.Series to boolean types.


.. py:function:: check_dataframe_coherence(data_df)
   :module: target.check_schema

   Dummy check to test dataframe wide checks, defined at the Schema level


.. py:function:: check_num_finess_format(num_finess_et: ~pandera.typing.pandas.Series[str]) -> ~pandera.typing.pandas.Series[bool]
   :module: target.check_schema

   Finess identifiers are 9 characters wide (alphanumerical)
