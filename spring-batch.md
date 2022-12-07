
# Job Parameters
## Run in Command Line
```
python3 /scripts/jobstart3.py customJob epochStart=1669765767000 epochEnd=1669938567000
```

Example given:
```
    public customJobReader(
            @Value("#{jobParameters.getOrDefault('epochStart', null)}") Long epochStart,
            @Value("#{jobParameters.getOrDefault('epochEnd', null)}") Long epochEnd,
            @Value("${endpoint.elasticsearch.index.customIndex}") String esIndexPrefix,
            @Autowired Elasticsearch elasticsearchService
    )
```
In Command Line:
```
clean spring-boot:run -Drun.arguments=epochStart=1667790578000,epochEnd=1667790578000 -Dspring.batch.job.names=customJob -Dspring.profiles.active=default,dev -f pom.xml
```

## Code
```
@Component
@StepScope
public class NewChangeReader implements ItemReader<Set<SnowTicket>> {

    static final Duration MAX_PER_DURATION = Duration.ofDays(1);

    String changeIndexPrefix;
    SnowService snowService;
    PoolMetadataProvider poolMetadataProvider;
    DataProvider dataProvider;
    EsService esService;
    ZonedDateTime start;
    ZonedDateTime end;

    ZonedDateTime currentHead;

    public NewChangeReader(
            @Value("#{jobParameters.getOrDefault('startTimestamp', null)}") Long startTimestamp,
            @Value("#{jobParameters.getOrDefault('endTimestamp', null)}") Long endTimestamp,
            @Value("${endpoint.elasticsearch.index.change}") String changeIndexPrefix,
            @Autowired SnowService snowService,
            @Autowired PoolMetadataProvider poolMetadataProvider,
            @Autowired DataProvider dataProvider,
            @Autowired EsService esService
    ) {
        this.changeIndexPrefix = changeIndexPrefix;
        this.snowService = snowService;
        this.poolMetadataProvider = poolMetadataProvider;
        this.dataProvider = dataProvider;
        this.esService = esService;
        if (startTimestamp == null) {
            this.start = ChangeEsUtil.getRemoteHead(
                    this.esService, this.changeIndexPrefix, ChangeType.CODE_ROLL, Constants.TIMESTAMP_FIELD_NAME);
        } else {
            this.start = ZonedDateTime.ofInstant(Instant.ofEpochMilli(startTimestamp), Constant.DEFAULT_ZONED_ID);
        }
        if (endTimestamp == null) {
            this.end = ZonedDateTime.now();
        } else {
            this.end = ZonedDateTime.ofInstant(Instant.ofEpochMilli(endTimestamp), Constant.DEFAULT_ZONED_ID);
        }
        this.currentHead = this.start;
        log.info(String.format("Start: %s; End: %s",
                this.start.format(DateTimeFormatter.ISO_DATE_TIME),
                this.end.format(DateTimeFormatter.ISO_DATE_TIME)
        ));
    }
```

# Two Item Writers
```
    @Bean
    public Job scrubChanges() {
        List<ItemWriter<? super Set<Change>>> writers = new ArrayList<>();
        writers.add(newChangeEsWriterV1);
        writers.add(newChangeEsWriterV2);
        CompositeItemWriter<Set<Change>> compositeItemWriter = new CompositeItemWriter<>();
        compositeItemWriter.setDelegates(writers);
        Step scrubChanges = stepBuilders
                .get("scrubChange")
                .<Set<SnowTicket>, Set<Change>>chunk(1)
                .reader(newChangeReader)
                .processor(newChangeProcessor)
                .writer(compositeItemWriter)
                .build();

        return jobBuilders.get("changeScrubber")
                .start(scrubChanges)
                .build();
    }
```
