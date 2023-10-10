# Sender
```
@Slf4j
@AllArgsConstructor
public class EsSender implements Sender {

    EsService esService;
    EsSenderConfigBean configBean;

    @Override
    public synchronized void send(Map<String, Object> data) {
        log.info("enabled={}, sampleBps={}.", configBean.isEnabled(), configBean.getSampleBps());
        if (configBean.isEnabled() && shouldSample()) {
            log.info("sending to ES");
            esService.index(configBean.getIndexName(), data);
        }
    }

    private boolean shouldSample() {
        return ThreadLocalRandom.current().nextDouble() <= configBean.getSampleBps() / 10000.0;
    }
}

```


# Consumer
```
package com.somecompany.app.someconsumer.consumer;

import com.somecompany.ads.common.api.client.elasticsearch.EsService;
import com.somecompany.app.someconsumer.configbean.ImaConsumerConfigBean;
import com.somecompany.app.someconsumer.configbean.ImaThreadPoolConfigBean;
import com.somecompany.app.someconsumer.core.PlacementMetaProvider;
import com.somecompany.dukes.CacheFactory;
import com.fasterxml.jackson.databind.ObjectMapper;
import io.somecompany.kafka.kafka.client.StreamConnectorConfig;
import io.somecompany.kafka.schema.avro.GenericRecordDomainDataDecoder;
import io.somecompany.kafka.schema.event.KafkaEvent;
import lombok.extern.slf4j.Slf4j;
import org.apache.kafka.clients.CommonClientConfigs;
import org.apache.kafka.clients.consumer.ConsumerConfig;
import org.apache.kafka.clients.consumer.KafkaConsumer;
import org.apache.kafka.common.config.SaslConfigs;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.CommandLineRunner;
import org.springframework.core.env.Environment;
import org.springframework.stereotype.Component;

import javax.annotation.PreDestroy;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Properties;
import java.util.Set;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.LinkedBlockingQueue;
import java.util.concurrent.ThreadPoolExecutor;
import java.util.concurrent.TimeUnit;

@Slf4j
@Component
public class ImaConsumer implements CommandLineRunner {

    private final Set<ConsumeTask> tasks = new HashSet<>();

    ImaConsumerConfigBean consumerConfigBean;
    ImaThreadPoolConfigBean threadPoolConfigBean;

    Properties kafkaProperties;
    GenericRecordDomainDataDecoder kafkaDecoder;

    Environment env;
    ObjectMapper objectMapper;
    CacheFactory nukvCacheFactory;
    PlacementMetaProvider placementMetaProvider;

    public ImaConsumer(
            @Value("${ima.kafka.bootstrapSevers}") String bootstrapSevers,
            @Value("${ima.kafka.decoder.url}") String decoderUrl,
            @Autowired Environment env,
            @Autowired ObjectMapper objectMapper,
            @Autowired ImaConsumerConfigBean consumerConfigBean,
            @Autowired ImaThreadPoolConfigBean threadPoolConfigBean,
            @Autowired EsService esService,
            @Autowired CacheFactory nukvCacheFactory,
            @Autowired PlacementMetaProvider placementMetaProvider
            ) {
        this.consumerConfigBean = consumerConfigBean;
        this.threadPoolConfigBean = threadPoolConfigBean;
        this.threadPoolConfigBean.addPropertyChangeListener(evt -> {
            log.info("ConfigBean property name {} tries to change from {} to {}",
                    evt.getPropertyName(), evt.getOldValue(), evt.getNewValue());
            stop();
            start();
        });
        this.env = env;
        this.objectMapper = objectMapper;
        this.nukvCacheFactory = nukvCacheFactory;
        this.placementMetaProvider = placementMetaProvider;

        Properties props = new Properties();
        props.put(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, bootstrapSevers);
        props.put(ConsumerConfig.GROUP_ID_CONFIG, "ads-infra-ima-raptor");
        props.put(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, "org.apache.kafka.common.serialization.ByteArrayDeserializer");
        props.put(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, "io.somecompany.kafka.schema.avro.KafkaEventDeserializer");
        props.put(ConsumerConfig.ENABLE_AUTO_COMMIT_CONFIG, "true");
        props.put(ConsumerConfig.AUTO_OFFSET_RESET_CONFIG, "latest");
        props.put(ConsumerConfig.RECEIVE_BUFFER_CONFIG, 4 * 1024 * 1024);
        props.put(ConsumerConfig.MAX_PARTITION_FETCH_BYTES_CONFIG, 4 * 1024 * 1024);
//        props.put(ConsumerConfig.PARTITION_ASSIGNMENT_STRATEGY_CONFIG, StickyAssignor.class.getName());
        props.put(ConsumerConfig.MAX_POLL_RECORDS_CONFIG, 5000);
        props.put(SaslConfigs.SASL_MECHANISM, "IAF");
        props.put(CommonClientConfigs.SECURITY_PROTOCOL_CONFIG, "SASL_PLAINTEXT");
        props.put(SaslConfigs.SASL_JAAS_CONFIG, "io.somecompany.kafka.kafka.security.iaf.login.RaptorioIAFLoginModule required;");

        this.kafkaProperties = props;

        Map<String, Object> config = new HashMap<>();
        config.put(StreamConnectorConfig.RHEOS_SERVICES_URLS, decoderUrl);
        this.kafkaDecoder = new GenericRecordDomainDataDecoder(config);
    }

    private void start() {
        log.info("start consume. ");
        log.info(String.format(
                "threadPoolSize=%s; queueSize=%s;",
                threadPoolConfigBean.getThreadCount(), threadPoolConfigBean.getQueueSize()));
        ExecutorService consumerPool = new ThreadPoolExecutor(
                threadPoolConfigBean.getThreadCount(), threadPoolConfigBean.getThreadCount() * 2,
                60L, TimeUnit.SECONDS,
                new LinkedBlockingQueue<>(threadPoolConfigBean.getQueueSize()));

        try {
            for (int i = 0; i < threadPoolConfigBean.getThreadCount(); i++) {
                KafkaConsumer<byte[], KafkaEvent> consumer = new KafkaConsumer<>(this.kafkaProperties);
                ConsumeTask task = new ConsumeTask(
                        consumer,
                        this.consumerConfigBean,
                        this.kafkaDecoder,
                        this.objectMapper,
                        this.env,
                        this.placementMetaProvider,
                        this.nukvCacheFactory
                );
                tasks.add(task);
                consumerPool.submit(task);
            }
        } catch (Exception e) {
            log.error("Submit consume task failed, error: {}", e.getMessage(), e);
        }
    }

    private void stop() {
        log.info("stop consume");
        tasks.forEach(ConsumeTask::stop);
        tasks.clear();
    }

    @Override
    public void run(String... args) throws Exception {
        start();
    }

    @PreDestroy
    public void destroy() {
        stop();
    }
}


```

# Consumer


```
package com.somecompany.app.someconsumer.consumer;

import com.somecompany.app.someconsumer.configbean.ImaConsumerConfigBean;
import com.somecompany.app.someconsumer.configbean.NukvSenderConfigBean;
import com.somecompany.app.someconsumer.configbean.UmpSenderConfigBean;
import com.somecompany.app.someconsumer.consumer.sender.NukvSender;
import com.somecompany.app.someconsumer.consumer.sender.Sender;
import com.somecompany.app.someconsumer.consumer.sender.UmpSender;
import com.somecompany.app.someconsumer.core.PlacementMetaProvider;
import com.somecompany.app.someconsumer.core.model.Placement;
import com.somecompany.app.someconsumer.event.EventDecoderJava;
import com.somecompany.app.someconsumer.event.soj.EventType$;
import com.somecompany.app.someconsumer.util.Utils;
import com.somecompany.dukes.CacheFactory;
import com.somecompany.kernel.bean.configuration.ConfigCategoryCreateException;
import com.somecompany.pl.poplex.model.flinpo.EventPayload;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.api.client.util.Strings;
import io.somecompany.kafka.schema.avro.GenericRecordDomainDataDecoder;
import io.somecompany.kafka.schema.event.KafkaEvent;
import io.micrometer.core.instrument.Metrics;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.EqualsAndHashCode;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.apache.avro.generic.GenericRecord;
import org.apache.avro.util.Utf8;
import org.apache.kafka.clients.consumer.ConsumerRecord;
import org.apache.kafka.clients.consumer.ConsumerRecords;
import org.apache.kafka.clients.consumer.KafkaConsumer;
import org.springframework.core.env.Environment;

import java.time.Duration;
import java.time.ZonedDateTime;
import java.util.Arrays;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.concurrent.TimeUnit;
import java.util.stream.Collectors;

@Slf4j
public class ConsumeTask implements Runnable {

    private static final String TOPIC = "behavior.pulsar.customized.pl_merch_ima";

    private static final String CLICK_NUKV_KEY_PREFIX = "event-ima";
    private static final String CLICK_LOG_FILE = "click";
    private static final String IMPRESSION_LOG_FILE = "impression";

    private static final Set<String> CARED_FIELDS = new HashSet<>(Arrays.asList(
            "algoId", "algoName", "browserFamily", "clickedItemId",
            "meid", "pageFamily", "pageId", "pageName", "userId",
            "placementId", "promoted", "sessionId", "eventTimestamp", "eventType", "amclksrc",
            "trackprov", "ampid", "medi"
    ));

    @Getter
    private volatile boolean terminated = false;
    private final ImpressionCache impressionCache = new ImpressionCache(Duration.ofSeconds(60), 3);

    KafkaConsumer<byte[], KafkaEvent> consumer;
    ImaConsumerConfigBean configBean;
    GenericRecordDomainDataDecoder decoder;
    PlacementMetaProvider placementMetaProvider;
    Sender clickNuKvSender;
    Sender clickUmpSender;
    Sender impressionUmpSender;

    public ConsumeTask(
            KafkaConsumer<byte[], KafkaEvent> consumer,
            ImaConsumerConfigBean consumerConfigBean,
            GenericRecordDomainDataDecoder decoder,
            ObjectMapper objectMapper,
            Environment env,
            PlacementMetaProvider placementMetaProvider,
            CacheFactory nukvCacheFactory
    ) {
        this.consumer = consumer;
        this.configBean = consumerConfigBean;
        this.decoder = decoder;
        this.placementMetaProvider = placementMetaProvider;
        try {

            NukvSenderConfigBean clickNukvSenderConfig = new NukvSenderConfigBean("clickNukvSenderConfig", CLICK_NUKV_KEY_PREFIX, 10000);
            this.clickNuKvSender = new NukvSender(objectMapper, nukvCacheFactory, clickNukvSenderConfig);
            UmpSenderConfigBean clickUmpSenderConfigBean = new UmpSenderConfigBean("clickUmpSenderConfig", 10000);
            this.clickUmpSender = new UmpSender(CLICK_LOG_FILE, clickUmpSenderConfigBean, objectMapper, env);

            UmpSenderConfigBean impressionUmpSenderConfigBean = new UmpSenderConfigBean("impressionUmpSenderConfig", 10000);
            this.impressionUmpSender = new UmpSender(IMPRESSION_LOG_FILE, impressionUmpSenderConfigBean, objectMapper, env);
        } catch (ConfigCategoryCreateException ex) {
            throw new RuntimeException("create config bean failed. ex=" + ex.getMessage());
        }
    }

    public void stop() {
        this.terminated = true;
    }

    @Override
    public void run() {
        this.consumer.subscribe(Collections.singletonList(TOPIC));
        while (true) {
            try {
                if (this.terminated) {
                    this.consumer.unsubscribe();
                    this.consumer.close();
                    handleImpression(this.impressionCache.forceFlushAll());
                    break;
                }
                ConsumerRecords<byte[], KafkaEvent> consumerRecords = consumer.poll(Duration.ofSeconds(30));
                log.info("Got {} records from {}", consumerRecords.count(), TOPIC);
                if (consumerRecords.isEmpty() && configBean.getSleepMsOnEmpty() > 0) {
                    log.info("{} sleep for {}ms.", Thread.currentThread().getName(), configBean.getSleepMsOnEmpty());
                    TimeUnit.MILLISECONDS.sleep(configBean.getSleepMsOnEmpty());
                } else {
                    for (ConsumerRecord<byte[], KafkaEvent> consumerRecord : consumerRecords) {
                        GenericRecord record = decoder.decode(consumerRecord.value());
                        Optional<EventPayload> dataOpt = EventDecoderJava.decode(record);
                        if (dataOpt.isPresent()) {
                            Map<String, Object> basicInfo = getBasicData(record);
                            EventDecoderJava.flatToMapSeq(dataOpt.get())
                                    .forEach(detail -> {
                                        Map<String, Object> finalData = new HashMap<>();
                                        finalData.putAll(basicInfo);
                                        finalData.putAll(detail);
                                        fillPageFamily(finalData);
                                        this.publish(dataOpt.get().eventTimestamp(), dataOpt.get().eventType(), finalData);
                                    });
                        }
                    }
                }
                handleImpression(impressionCache.flush());
            } catch (Exception e) {
                log.error(e.getMessage(), e);
            }
        }
    }

    private void publish(long eventTimestamp, String eventTypeStr, Map<String, Object> data) {
        if (EventType$.MODULE$.isClickEvent(eventTypeStr)) {
            try {
                this.clickUmpSender.send(data);
            } catch (Exception ex) {
                log.error("ClickUmpSender failed to send click. ex=" + ex.getMessage());
            }
            try {
                this.clickNuKvSender.send(data);
            } catch (Exception ex) {
                log.error("ClickNuKvSender failed to send click. ex=" + ex.getMessage());
            }
        }
        if (EventType$.MODULE$.isImpressionEvent(eventTypeStr)) {
            String placementId = data.get("placementId") == null ? "" : data.get("placementId").toString();
            String siteId = data.get("siteId") == null ? "" : data.get("siteId").toString();
            String pageId = data.get("pageId") == null ? "" : data.get("pageId").toString();
            ImpressionDimension dimension = new ImpressionDimension(eventTypeStr, siteId, pageId, placementId);
            impressionCache.add(eventTimestamp, dimension);
        }
    }

    private void handleImpression(Set<Map.Entry<Long, Map<ImpressionDimension, Integer>>> dataFrames) {
        dataFrames.forEach(dataFrame -> {
            long timestamp = dataFrame.getKey();
            Map<ImpressionDimension, Integer> dataPoints = dataFrame.getValue();
            dataPoints.forEach(((dimension, count) -> {
                try {
                    Map<String, Object> data = new HashMap<>();
                    data.put("timestamp", timestamp);
                    data.put("eventType", dimension.getEventType());
                    data.put("placementId", dimension.getPlacementId());
                    data.put("count", count);
                    this.impressionUmpSender.send(data);
                } catch (Exception ex) {
                    log.error("ImpressionUmpSender failed to send impression. ex=" + ex.getMessage());
                }
            }));
        });
    }

    // applicationPayload sample:
    // {nqc=AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAQAAAAABAAAAAAAAAAAAAAAAACAAAAAAAAAAAAAAAAAAAAAAAAAABAAAAAAAAAAAAQAAABAEAAJAEgAAAAAAMAAUAAAAAgAAAAAIAAAAAAAAwCBCAAFAAgIAgABQEEABAAAAAACAAAAAAAAIAAQAAAAAAAAAAAAAAAAACAAABAAgAAIAAEAAAAAAABAAAAAAgBVVShIJEAAACAgABQAAIAAAAAKAAQAQAAQAACABIAiAAAASRA*,
    // screenScale=3.0, rdt=0, rlogid=t6faabwwmtuf0*fkpa4oilh0%3Fqk%3F%3Ckuvccd%60ruhvpd5%28%3Ee6hu*w%60ut3457-183ae5ee405-0x2339,
    // formFactor=phone, tz=-07%3A00, dm=Apple, dn=iPhone13_2, inputCorrelator=3, moduledtl=mi%3A4519%7Ciid%3A1,
    // js_ev_mak=b57be2f218004b4cb04557d0016b1534, pageName=Ginger.tracking.v1.batchtrack.POST, uc=3, mos=iOS,
    // nqt=AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAQAAAAABAAAAAAAAAAAAAABAACAAAAAAAAAAAAAAAAAAAAAAAAAABAAAAAAAAAAAAQAAABAEBAJAEgAAAAAAMAAUAAAAAgAAAAAIAAAAAAAAwCBCAAFAAgIAgABQEEABAAAAAACAAAAAAAAIAESCAAAAAAgAAAkIAAAACCTCRAAgAAKAAEAAAAAAgVBJRKAAgBVVShJJMgAACCgABQAAIAAAAAKAAQAQAAQAACABIAiAAAASRA*,
    // osv=15.6.1, pageci=6a4cbfb8-459d-11ed-a012-9e9ed8a40fc1, ul=en-US, clientIP=67.161.99.82,
    // callingpagename=hpservice__experience_search_v1_get_homepage_search_result_GET, kafkaUpstreamSendTs=1665077797954,
    // windowWidth=390, mtsts=2022-10-06T17%3A36%3A31.762Z, ec=5, app=1462, res=390X844,
    // Agent=somecompanyUserAgent/eBayIOS;6.80.0;iOS;15.6.1;Apple;iPhone13_2;Xfinity Mobile;390x844;3.0,
    // efam=HOMEPAGE, bott=0, corrId=1ba087f873b2bcde, idfa=00000000-0000-0000-0000-000000000000,
    // eprlogid=t6fuuq%60%28ciuc1mlnm2%3Asn%3D9iptfuuq%60%28uauwa*w%60ut3512-183ae5eca72-0xcd, ifrm=true,
    // es=3, dd_dc=null null null, mdbreftime=1665076989449, dd_os=Other, Payload=/base/tracking/v1/batchtrack,
    // mrollp=98, eactn=VIEW, gitCommitId=5a62e6386225586f9c73d83f244b4050ef1c6f50, nodeId=0dda78703f929cfb,
    // rq=1ba087f873b2bcde, epcalenv=core_staging, rv=true, RemoteIP=67.161.99.82, windowHeight=844, cbrnd=6,
    // js_sojuuid=9f55a29d-6f12-4a26-96de-97170878d4ab, dd_d=Mobile, tzname=America%2FLos_Angeles, dd_bf=Other,
    // deviceAdvertisingOptOut=true, ampid=MADRONA, EventTS=10:36:37.89, TPool=r1edgetrksvc6-envf7jokk59vh,
    // theme=light, ammiid=4244058464393168217, ForwardedFor=10.222.16.203, pagename=PulsarGateway,
    // timestamp=1665077791762, uit=1664216224000, parentrq=O31NbTStDYMB4e1b, mav=6.80.0,
    // amdata=uid%3D45587560865%7Cbs%3D3%7Ct%3D3%7Ctdt%3Diid%3A4244058464393168217%2Cclkid%3
    //  A4244058464393168216%7Cbw%3DSMALL%7Cplmt%3D%28channel%3ANATIVE_APP+cnv.cfg.id%3AMOCK_
    //  CANVAS_CONFIGURATION_ID+cnv.ctx.id%3AMOCK_CANVAS_CONTEXT_ID+cnv.id%3A100003+iid%3A424
    //  4058464393168217+isUEP%3A1+mesg.id%3A3188668064998597760+message.mob.trk.id%3AMOCK-TR
    //  ACCKING-ID+pageci%3Afcbe11b7-9fac-467f-a355-dd8a67759305+parentrq%3AO31NbTStDYMB4e1b+
    //  plmt.id%3A100025+send.trk.id%3AMOCK-TRACCKING-ID+site.id%3A3%29%7Cul%3Den-US%7Cguid%3D
    //  b57be2f218004b4cb04557d0016b1534%7Cuc%3D3%7Ccr.id%3D7729289401241625149%7Ccr.vt.id%3D16
    //  53004517110%7CmobtrkId%3Ddd90ae9a-c381-48da-860e-557e10c812bc%7EsAi6hM8JmYUNHwT8OvQGeLj9
    //  jO4SeWmPj3RyScigTjh%7EGEmWzRtQRUPOs77AQqkA62XRBm4Xjg4MwPqdEuxnapZ,
    // g=b57be2f218004b4cb04557d0016b1534, h=f2, Referer=, TType=URL, gbh=1, nativeApp=true, cp=2481888,
    // urlQueryString=/base/tracking/v1/batchtrack, p=2356359, mnt=wifi, carrier=Xfinity+Mobile,
    // kafkaUpstreamCreateTs=1665077791762, t=3, u=2466454732, ts=2022-10-06T17%3A36%3A31.762Z}
    private Map<String, Object> getBasicData(GenericRecord record) {
        Map<Utf8, Utf8> applicationPayload = null;
        try {
            applicationPayload = (HashMap<Utf8, Utf8>) record.get("applicationPayload");
        } catch (Exception ex) {
            log.error("applicationPayload is not map. ex=" + ex.getMessage());
        }
        Map<String, Object> data = new HashMap<>();
        for (String s : CARED_FIELDS) {
            String value = null;
            if (record.hasField(s) && record.get(s) != null) {
                value = record.get(s).toString();
            }
            if (value == null && applicationPayload != null && applicationPayload.get(new Utf8(s)) != null) {
                value = applicationPayload.get(new Utf8(s)).toString();
            }
            data.put(s, value);
        }
        return data;
    }

    private void fillPageFamily(Map<String, Object> data) {
        data.put("pageFamily", "");
        Object placementIdObj = data.get("placementId");
        if (placementIdObj == null || Strings.isNullOrEmpty(placementIdObj.toString())) {
            return;
        }
        Placement pl = this.placementMetaProvider.getPlacement(placementIdObj.toString());
        if (pl == null) {
            Metrics.counter("missing_placement_meta",
                    "placementId", placementIdObj.toString(),
                    "pageId", Utils.getOrDefault(data, "pageId", "").toString()
            ).increment();
            return;
        }
        if (pl.getPageFamily() != null) {
            data.put("pageFamily", pl.getPageFamily().toLowerCase());
        }
    }

    @Data
    @EqualsAndHashCode
    @AllArgsConstructor
    @NoArgsConstructor
    static class ImpressionDimension {
        String eventType;
        String siteId;
        String pageId;
        String placementId;
    }

    // not thread safe !
    // this is used only in one Runnable/Thread
    private static class ImpressionCache {

        Map<Long, Map<ImpressionDimension, Integer>> cache = new HashMap<>();
        final Duration step;
        final int maxSteps;

        public ImpressionCache(Duration step, int maxSteps) {
            this.step = step;
            this.maxSteps = maxSteps;
        }

        // seconds
        public void add(long timestamp,  ImpressionDimension dimension) {
            long key = roundTimestampToKey(timestamp);
            Map<ImpressionDimension, Integer> existingValue = cache.get(key);
            if (existingValue == null) {
                existingValue = new HashMap<>();
            }
            Integer existingCount = existingValue.get(dimension);
            if (existingCount == null) {
                existingCount = 0;
            }
            int newCount = existingCount + 1;
            existingValue.put(dimension, newCount);
            cache.put(key, existingValue);
        }

        public Set<Map.Entry<Long, Map<ImpressionDimension, Integer>>> flush() {
            long expiration = ZonedDateTime.now().toInstant().toEpochMilli() - this.step.toMillis() * this.maxSteps;
            Set<Map.Entry<Long, Map<ImpressionDimension, Integer>>> result = cache.entrySet()
                    .stream()
                    .filter(e -> e.getKey() < expiration)
                    .collect(Collectors.toSet());
            if (!result.isEmpty()) {
                result.forEach(e -> cache.remove(e.getKey()));
                log.info("flush. expiration={}", expiration);
            }
            return result;
        }

        public Set<Map.Entry<Long, Map<ImpressionDimension, Integer>>> forceFlushAll() {
            log.info("force flush all impression cache");
            Set<Map.Entry<Long, Map<ImpressionDimension, Integer>>> result = this.cache.entrySet();
            cache = new HashMap<>();
            return result;
        }

        private long roundTimestampToKey(long timestamp) {
            return timestamp / step.toMillis() * step.toMillis();
        }
    }
}
```
