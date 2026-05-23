# JVM Artifact Capture Flags

Use these flags before reproducing an OOM or memory-retention incident:

```text
-Xlog:gc*:file=/path/to/jvm-logs/gc-%p.log:time,uptime,level,tags
-XX:+HeapDumpOnOutOfMemoryError
-XX:HeapDumpPath=/path/to/jvm-logs/
```

Recommended additions for repeatable incident capture:

```text
-XX:+ExitOnOutOfMemoryError
-XX:ErrorFile=/path/to/jvm-logs/hs_err_pid%p.log
```

For Maven Surefire/Failsafe:

```xml
<argLine>
  -Xmx8g
  -Xlog:gc*:file=${project.build.directory}/jvm-logs/gc-%p.log:time,uptime,level,tags
  -XX:+HeapDumpOnOutOfMemoryError
  -XX:HeapDumpPath=${project.build.directory}/jvm-logs/
</argLine>
```

For Gradle test tasks:

```groovy
test {
  jvmArgs '-Xmx8g',
          '-Xlog:gc*:file=build/jvm-logs/gc-%p.log:time,uptime,level,tags',
          '-XX:+HeapDumpOnOutOfMemoryError',
          '-XX:HeapDumpPath=build/jvm-logs/'
}
```

Notes:

- Keep the GC log and heap dump from the same process run.
- Use `%p` in file names when multiple JVMs may run at the same time.
- Preserve the original heap dump timestamp when possible. If files are copied
  or archived, pass the real capture time through `--dump-time`.
