using Dapper;
using Npgsql;

namespace Roblox.Services;

public static class Database
{
    private static string dbConnectionString { get; set; } = string.Empty;
    private static Mutex connectionMutex { get; } = new();

    public static void AcquireConnectionMutex(string debugReason)
    {
        connectionMutex.WaitOne();
    }

    public static void ReleaseConnectionMutex()
    {
        connectionMutex.ReleaseMutex();
    }

    public static NpgsqlConnection connection
    {
        get
        {
            AcquireConnectionMutex("Database.connection");
            var myConn = unsafeConnection;
            ReleaseConnectionMutex();
            return myConn;
        }
    }
    
    public static NpgsqlConnection unsafeConnection => new NpgsqlConnection(dbConnectionString);

    /// <summary>
    /// List of table names, use for preparing statements
    /// </summary>
    public static List<string> tableNames { get; set; } = new();

    /// <summary>
    /// A dictionary of tableName to tableColumns
    /// </summary>
    public static Dictionary<string, List<string>> tableToColumnMap { get; set; } = new();
    public static void Configure(string databaseConnectionString)
    {
        dbConnectionString = databaseConnectionString;

        // The first query after PostgreSQL starts (especially after crash recovery) can be slow
        // while Npgsql loads the type catalog. Retry with a generous timeout instead of crashing.
        var startupConnectionString = new NpgsqlConnectionStringBuilder(dbConnectionString)
        {
            Timeout = 30,
            CommandTimeout = 120,
            Pooling = false,
        }.ConnectionString;
        List<dynamic> columns = null!;
        for (var attempt = 1; ; attempt++)
        {
            try
            {
                using var db = new NpgsqlConnection(startupConnectionString);
                columns = db.Query("SELECT table_name, column_name FROM information_schema.columns WHERE table_schema = 'public' AND table_catalog = current_database() ORDER BY table_name, ordinal_position", commandTimeout: 120).ToList();
                break;
            }
            catch (Exception e) when (attempt < 6 && (e is NpgsqlException || e is TimeoutException))
            {
                Console.WriteLine($"[Database] schema load attempt {attempt} failed ({e.GetType().Name}); retrying");
                Thread.Sleep(TimeSpan.FromSeconds(5 * attempt));
            }
        }
        tableNames.Clear();
        tableToColumnMap.Clear();
        foreach (var column in columns)
        {
            string table = column.table_name;
            if (!tableToColumnMap.ContainsKey(table))
            {
                tableNames.Add(table);
                tableToColumnMap[table] = new List<string>();
            }
            tableToColumnMap[table].Add((string)column.column_name);
        }
        // Dapper config here
        Dapper.DefaultTypeMap.MatchNamesWithUnderscores = true;
    }
}
