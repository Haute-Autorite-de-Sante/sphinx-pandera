
.. py:module:: target.index_model


.. py:pandera_model:: TestMultiIndexModel
   :module: target.index_model

   Model with two fields which are a pandas index (multiIndex)


   .. py:pandera_model_config:: TestMultiIndexModel.Config
      :module: target.index_model


      .. py:attribute:: TestMultiIndexModel.Config.strict
         :module: target.index_model


      .. py:attribute:: TestMultiIndexModel.Config.coerce
         :module: target.index_model


   .. py:pandera_field:: TestMultiIndexModel.key1
      :module: target.index_model
      :type: ~pandera.typing.pandas.Index[str]
      :title: First Index type field

      Field whose dtype is Index


      :Constraints:
         - **nullable** = False
         - **unique** = True
         - **coerce** = False
         - **required** = True (Index)
      :Validated by:
         - **str_matches('^AIPE-[0-9]+$')**

   .. py:pandera_field:: TestMultiIndexModel.key2
      :module: target.index_model
      :type: ~pandera.typing.pandas.Index[str]
      :title: Second Index type field

      Field whose dtype is Index


      :Constraints:
         - **nullable** = False
         - **unique** = True
         - **coerce** = False
         - **required** = True (Index)
      :Validated by:
         - **str_matches('^AIPE2-[0-9]+$')**

.. py:pandera_model:: TestSingleIndexModel
   :module: target.index_model

   Model with a single field which is a pandas index


   .. py:pandera_model_config:: TestSingleIndexModel.Config
      :module: target.index_model


      .. py:attribute:: TestSingleIndexModel.Config.strict
         :module: target.index_model


      .. py:attribute:: TestSingleIndexModel.Config.coerce
         :module: target.index_model


   .. py:pandera_field:: TestSingleIndexModel.key
      :module: target.index_model
      :type: ~pandera.typing.pandas.Index[str]
      :title: First Index type field

      Field whose dtype is Index


      :Constraints:
         - **nullable** = False
         - **unique** = True
         - **coerce** = False
         - **required** = True (Index)
      :Validated by:
         - **str_matches('^AIPE-[0-9]+$')**