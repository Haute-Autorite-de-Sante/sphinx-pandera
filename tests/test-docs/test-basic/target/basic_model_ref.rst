
.. py:module:: target.basic_model


.. py:pandera_model:: TestModel
   :module: target.basic_model

   First data model for testing purposes


   .. py:pandera_field:: TestModel.field1
      :module: target.basic_model
      :type: int
      :title: Field 1 Title

      My field description


      :Constraints:
         - **nullable** = False
         - **unique** = False
         - **coerce** = False
         - **required** = True

   .. py:pandera_model_config:: TestModel.Config
      :module: target.basic_model
      :canonical: pandera.api.dataframe.model.Config


      .. py:attribute:: TestModel.Config.coerce
         :module: target.basic_model
         :type: bool

         coerce types of all schema components


      .. py:attribute:: TestModel.Config.ordered
         :module: target.basic_model
         :type: bool

         validate columns order


      .. py:attribute:: TestModel.Config.strict
         :module: target.basic_model
         :type: StrictType

         make sure all specified columns are in the validated dataframe -
         if ``"filter"``, removes columns not specified in the schema
