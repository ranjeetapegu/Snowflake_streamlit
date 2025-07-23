use role fr_scientist
use database ml_models;
use schema ds;

create stage ml_models.ds.image_files 
  ENCRYPTION = (TYPE = 'SNOWFLAKE_SSE');

  //select the image from the drop-down
  SELECT * FROM DIRECTORY( @ml_models.ds.image_files)

  // select the model 

//Upload the image using snowflake snowsight GUI - download from the Data folder //

