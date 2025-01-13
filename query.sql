WITH CTE AS (
    SELECT TOP 3 
        [employeeid] AS employeeId,
        [eventtime] AS eventTime,
        [isCheckIn] AS isCheckin,
        [donwloaddate] AS downloaddate
    FROM [attendance]
	WHERE [zohopeople] is null
)
UPDATE [attendance]
SET [zohopeople] = 1
OUTPUT 
    INSERTED.[employeeid] AS employeeId,
    INSERTED.[eventtime] AS eventTime,
    INSERTED.[isCheckIn] AS isCheckin,
    INSERTED.[donwloaddate] AS downloaddate
FROM (
    SELECT * FROM CTE
) AS otherTable
WHERE 
    [attendance].[employeeid] = [otherTable].[employeeid]
    AND [attendance].[eventtime] = [otherTable].[eventtime]
    AND [attendance].[isCheckIn] = [otherTable].[isCheckIn]
    AND [attendance].[donwloaddate] = [otherTable].[downloaddate];
