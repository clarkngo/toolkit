```
package com.company.app.adsinfranumsgconsumer.consumer;

import com.company.adsinfra.common.api.client.elasticsearch.EsService;
import com.company.app.adsinfranumsgconsumer.configbean.ImaConsumerConfigBean;
import com.company.app.adsinfranumsgconsumer.configbean.ImaThreadPoolConfigBean;
import com.company.app.adsinfranumsgconsumer.core.PlacementMetaProvider;
import com.company.dukes.CacheFactory;
import com.fasterxml.jackson.databind.ObjectMapper;
import io.company.kafka.kafka.client.StreamConnectorConfig;
import io.company.kafka.schema.avro.GenericRecordDomainDataDecoder;
import io.company.kafka.schema.event.KafkaEvent;
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
        props.put(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, "io.company.kafka.schema.avro.KafkaEventDeserializer");
        props.put(ConsumerConfig.ENABLE_AUTO_COMMIT_CONFIG, "true");
        props.put(ConsumerConfig.AUTO_OFFSET_RESET_CONFIG, "latest");
        props.put(ConsumerConfig.RECEIVE_BUFFER_CONFIG, 4 * 1024 * 1024);
        props.put(ConsumerConfig.MAX_PARTITION_FETCH_BYTES_CONFIG, 4 * 1024 * 1024);
//        props.put(ConsumerConfig.PARTITION_ASSIGNMENT_STRATEGY_CONFIG, StickyAssignor.class.getName());
        props.put(ConsumerConfig.MAX_POLL_RECORDS_CONFIG, 5000);
        props.put(SaslConfigs.SASL_MECHANISM, "IAF");
        props.put(CommonClientConfigs.SECURITY_PROTOCOL_CONFIG, "SASL_PLAINTEXT");
        props.put(SaslConfigs.SASL_JAAS_CONFIG, "io.company.kafka.kafka.security.iaf.login.RaptorioIAFLoginModule required;");

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
