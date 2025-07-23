-- Step 1: Create the table
CREATE OR REPLACE TABLE system_status (
    system_name STRING,
    created_date DATE,
    update_date DATE,
    status STRING
);

-- Step 2: Insert 5 rows of sample data
INSERT INTO system_status (system_name, created_date, update_date, status)
VALUES
    ('System_A', '2024-01-10', '2024-07-10', 'Active'),
    ('System_B', '2023-11-05', '2024-06-15', 'Inactive'),
    ('System_C', '2024-03-22', '2025-01-12', 'Active'),
    ('System_D', '2022-09-30', '2023-12-01', 'Retired'),
    ('System_E', '2025-02-14', '2025-07-01', 'Maintenance');

select * from system_status;

/* create tasks that update the tables*/

CREATE OR REPLACE TASK task_1
  WAREHOUSE = ml_fs_w  -- Replace with your actual warehouse
  SCHEDULE = '3 minute'  -- Optional: adjust as needed
AS
  UPDATE system_status
  SET status = 'Updating'
  WHERE  status IN ('Inactive', 'Retired');

alter task task_1 resume;
EXECUTE TASK task_1 ;

/*task2*/
CREATE OR REPLACE TASK task_2
  WAREHOUSE = ml_fs_w  -- Replace with your actual warehouse
  SCHEDULE = '5 minute'  -- Optional: adjust as needed
AS
  UPDATE system_status
  SET status = 'Active'
  WHERE  status IN ('Updating');

    alter task task_2 resume

EXECUTE TASK task_2 ;

  
/*task3*/
    CREATE OR REPLACE TASK task_3
  WAREHOUSE = ml_fs_w  -- Replace with your actual warehouse
  SCHEDULE = '5 minute'  -- Optional: adjust as needed
AS
  UPDATE system_status
  SET status = 'Inactive'
  WHERE  status IN ('Active');

      alter task task_3 resume;
      EXECUTE TASK task_3;

-----don't forgot the disable task after completing the experiment
ALTER TASK task_1 suspend;
ALTER TASK  task_2 suspend;
ALTER TASK  task_3 suspend;
