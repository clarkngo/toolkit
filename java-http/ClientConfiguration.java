package com.examplecompany.adsinfra.common.autoconfiguration;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.extern.slf4j.Slf4j;
import org.glassfish.jersey.client.ClientProperties;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Lazy;
import org.springframework.context.annotation.Primary;
import org.springframework.core.env.Environment;

import javax.ws.rs.client.Client;
import javax.ws.rs.client.WebTarget;
import java.util.Arrays;

@Slf4j
@Configuration
@ConfigurationProperties(prefix="commonconfig")
public class ClientConfiguration {
    // GlobalConfig Repo https://github.corp.examplecompany.com/company/commonconfig
    private final static String GlobalConfig = "commonconfig.";

    private static final String ADSSRE_SamPath = "share/service_account/team_org";
    private static final String AdsQualityEsCred_SamPath = "share/service_account/es_indexname";
    private static final String SNOW_SamPath = "share/snow_account/path";
    public static final String APPLICATION_ID = "urn:examplecompany-consumerid:dc9e0993a6bc";

    @Autowired
    Environment env;
    ObjectMapper objectMapper = Util.getDefaultObjectMapper();

    @Autowired
    ICalEventHelper calEventHelper;
    @Autowired
    ICalEventFactory calEventFactory;
    @Autowired
    ICalTransactionFactory calTransactionFactory;

    private <T extends CalLogger> T injectCal(T logger) {
        logger.setCalEventFactory(calEventFactory);
        logger.setCalEventHelper(calEventHelper);
        logger.setCalTransactionFactory(calTransactionFactory);
        return logger;
    }

    private boolean isDev() {
        return Arrays.stream(env.getActiveProfiles())
                .noneMatch(p -> "pre-production".equalsIgnoreCase(p) || "production".equalsIgnoreCase(p));
    }

    private boolean isProdEnv() {
        return Arrays.stream(env.getActiveProfiles()).anyMatch("production"::equalsIgnoreCase);
    }

    private boolean isPreProd() {
        return Arrays.stream(env.getActiveProfiles())
                .anyMatch("pre-production"::equalsIgnoreCase);
    }

    private String getEnvProperty(String key) {
        String value = env.getProperty(key);
        if (value == null) value = env.getProperty(GlobalConfig+key);
        log.info(String.format("Get value from global config. key=%s, value=%s", key, value));
        return value;
    }

    private PasswordCredential getPasswordCredentialBySamPath(String samPath) {
        try {
            PasswordCredential pass = objectMapper.readValue(defaultSamInforProvider().getSamInfo(samPath),
                    PasswordCredential.class);
            log.info(String.valueOf(pass));
            return pass;
        } catch (JsonProcessingException e) {
            log.error(e.toString());
            return new PasswordCredential("", "");
        }
    }

    @Lazy
    @Bean
    @Primary
    public KeystoneService defaultKeystoneService() {
        Client client = HttpClientHelper.produceDefaultClient("keystoneService.teamname");
        WebTarget webTarget = client.target(getEnvProperty("uri.keystone_service"));
        return injectCal(new KeystoneService(webTarget, getPasswordCredentialBySamPath(ADSSRE_SamPath)));
    }

    @Lazy
    @Bean
    @Primary
    public EsService defaultEs() throws JsonProcessingException {
        if (isDev()) {
            Client client = HttpClientHelper.produceDefaultClient("defaultEs.dev");
            WebTarget webTarget = client.target(getEnvProperty("uri.kibana.defaultes"));
            return injectCal(new EsService(webTarget, getPasswordCredentialBySamPath(ADSSRE_SamPath)));
        } else {
            return productionAdsQualityEs();
        }
    }

    @Lazy
    @Bean(name = "productionDefaultEs")
    public EsService productionDefaultEs() {
        Client client = HttpClientHelper.produceDefaultClient("defaultEs.production");
        client.property(ClientProperties.READ_TIMEOUT, 60 * 1000);
        if (isDev()) {
            HttpClientHelper.attachC2sProxy(client);
        }
        WebTarget webTarget = client.target(getEnvProperty("uri.kibana.defaultes.prod"));
        return injectCal(new EsService(webTarget, getPasswordCredentialBySamPath(AdsQualityEsCred_SamPath)));
    }

    @Lazy
    @Bean
    @Primary
    public CmService defaultCmService() {
        return injectCal(new CmService(
                getEnvProperty("uri.cm_service"),
                defaultKeystoneService()
        ));
    }

    @Lazy
    @Bean
    @Qualifier("extended")
    public CmService extendedCmService() {
        return new CmService(
                getEnvProperty("uri.cm_service"),
                defaultKeystoneService(),
                defaultCmpaasService()
        );
    }

    @Lazy
    @Bean
    @Primary
    public EgressEventService defaultEgressEventService() {
        Client client = HttpClientHelper.produceDefaultClient("egressService.adsinfra");
        client.property(ClientProperties.READ_TIMEOUT, 60 * 1000);
        if (isDev()) {
            HttpClientHelper.attachC2sProxy(client);
        }
        WebTarget webTarget = client.target("https://monitoring-event-egress.vip.examplecompany.com"); // for event
        return injectCal(new EgressEventService(
                webTarget,
                defaultKeystoneService()
        ));
    }
    @Lazy
    @Bean
    @Primary
    public EgressMetricService defaultEgressMetricService() {
        Client client = HttpClientHelper.produceDefaultClient("egressServiceEvent.teamname");
        client.property(ClientProperties.READ_TIMEOUT, 60 * 1000);
        if (isDev()) {
            HttpClientHelper.attachC2sProxy(client);
        }
        WebTarget webTarget = client.target("https://query-frontend.monitoring-service.vip.examplecompany.com"); // for metrics
        return injectCal(new EgressMetricService(
                webTarget,
                defaultKeystoneService()
        ));
    }

    // pulse can't be accessed on production
    @Lazy
    @Bean
    @Primary
    public PulseService defaultPulseService() {
        Client client = HttpClientHelper.produceDefaultClient("pulseService.teamname");
        WebTarget webTarget = client.target(getEnvProperty("uri.pulse_service"));
        return injectCal(new PulseService(webTarget));
    }

    /**
     * @deprecated
     * Use {@link #productionNucolumnarReadAds()} instead.
     **/
    @Lazy
    @Bean
    @Primary
    @Deprecated
    public SellerhubClickmeService defaultSellClickMeService() {
        Client client = HttpClientHelper.produceDefaultClient("sellClickMeService.teamname");
        if (isDev()) {
            HttpClientHelper.attachC2sProxy(client);
        }
        client.property(ClientProperties.READ_TIMEOUT, 60 * 1000);
        WebTarget webTarget = client.target(getEnvProperty("uri.sellerhub_clickme_service"));
        return injectCal(new SellerhubClickhouseService(webTarget));
    }

    @Lazy
    @Bean
    @Primary
    public SnowService defaultServicenowService() {
        Client client = HttpClientHelper.produceDefaultClient("servicenowService.teamname");
        if (!isDev()) {
            HttpClientHelper.attachProductionOutboundProxy(client);
        }
        WebTarget webTarget = client.target(getEnvProperty("uri.servicenow_service"));
        return injectCal(new SnowService(webTarget, getPasswordCredentialBySamPath(SNOW_SamPath)));
    }

    @Lazy
    @Bean
    @Primary
    public TouchstoneService defaultTouchService() {
        Client client = HttpClientHelper.produceDefaultClient("touchService.teamname");
        if (isDev()) {
            HttpClientHelper.attachC2sProxy(client);
        }
        WebTarget webTarget = client.target(getEnvProperty("uri.touch_service"));
        return injectCal(new TouchstoneService(webTarget));
    }


    @Lazy
    @Bean
    @Primary
    public MetadataService defaultMetadataService() {
        String clientKey = "metadataService.teamname";
        Client client = HttpClientHelper.produceDefaultClient(clientKey);
        client.property(ClientProperties.READ_TIMEOUT, 60 * 1000);
        WebTarget webTarget = client.target(getEnvProperty("uri.metadataservice"));
        log.info(clientKey + ":uri: " + webTarget.getUri());
        return injectCal(new AdsmetadataService(webTarget));
    }

    @Lazy
    @Bean
    @Primary
    public SamInforProvider defaultSamInforProvider() {
        return injectCal(new SamInforProvider(defaultAdsmetadataService()));
    }

    @Lazy
    @Bean
    @Primary
    public COSTokenProvider defaultCOSTokenProvider() {
        return injectCal(new COSTokenProvider());
    }

    @Lazy
    @Bean
    @Primary
    public AdsCalLogger defaultCalLogger() {
        return new AdsCalLogger(calEventHelper, calEventFactory,  calTransactionFactory);
    }
}
