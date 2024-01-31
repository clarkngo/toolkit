package com..adsinfra.common.api.client;

// more imports

import lombok.extern.slf4j.Slf4j;
import org.apache.http.config.Registry;
import org.apache.http.config.RegistryBuilder;
import org.apache.http.conn.socket.ConnectionSocketFactory;
import org.apache.http.conn.socket.LayeredConnectionSocketFactory;
import org.apache.http.conn.socket.PlainConnectionSocketFactory;
import org.apache.http.conn.ssl.SSLConnectionSocketFactory;
import org.apache.http.impl.conn.PoolingHttpClientConnectionManager;
import org.glassfish.jersey.apache.connector.ApacheClientProperties;
import org.glassfish.jersey.apache.connector.ApacheConnectorProvider;
import org.glassfish.jersey.client.ClientProperties;
import org.glassfish.jersey.client.HttpUrlConnectorProvider;

import javax.net.ssl.HttpsURLConnection;
import javax.net.ssl.SSLContext;
import javax.ws.rs.client.Client;
import javax.ws.rs.core.Configuration;

@Slf4j
public class HttpClientHelper {

    private static final String ENV_NAME_C2S_USERNAME = "C2S_USERNAME";
    private static final String ENV_NAME_C2S_TOKEN = "C2S_TOKEN";
    private static final String C2S_PROXY_ENDPOINT = "http://c2syubi.vip.company.com:8080";
    private static final String PRODUCTION_OUTBOUND_PROXY_ENDPOINT = "http://httpproxy-tcop.vip.company.com:80";

    // clientKey should be unique
    public static Client produceDefaultClient(String clientKey) {
        Client client = createNewGingerClient(clientKey);
        addGingerClientDefaultSettings(client);
        addJsonSettings(client);
        return client;
    }

    // it might be always 407 when calling http (not https) endpoint on production.
    // it seems to be the issue about calling http endpoint over https proxy (c2sproxy is a https proxy).
    // so better all using https endpoint on production
    public static Client attachC2sProxy(Client client) {
        String c2sUsername = System.getenv(ENV_NAME_C2S_USERNAME);
        String c2sToken = System.getenv(ENV_NAME_C2S_TOKEN);
        if (c2sUsername == null || c2sToken == null) {
            log.error("Please set system env: 'C2S_USERNAME' and 'C2S_TOKEN' before attaching c2sProxy.");
        } else {
            client.property(ClientProperties.PROXY_URI, C2S_PROXY_ENDPOINT);
            client.property(ClientProperties.PROXY_USERNAME, c2sUsername);
            client.property(ClientProperties.PROXY_PASSWORD,c2sToken);
            client.property(ClientProperties.CONNECT_TIMEOUT, 5 * 1000);
            client.property(ClientProperties.READ_TIMEOUT, 60 * 1000);
            // do not use HttpUrlConnectorProvider here because it has something wrong about proxy
            try {
                SSLContext sc = SSLContext.getInstance("SSL");
                sc.init(null, SSLUtil.getTrustAllCert(), new java.security.SecureRandom());
                LayeredConnectionSocketFactory sslSocketFactory = new SSLConnectionSocketFactory(
                        sc,
                        SSLUtil.getTrustAllHostname()
                );
                final Registry<ConnectionSocketFactory> registry = RegistryBuilder.<ConnectionSocketFactory>create()
                        .register("http", PlainConnectionSocketFactory.getSocketFactory())
                        .register("https", sslSocketFactory)
                        .build();

                client.property(ApacheClientProperties.CONNECTION_MANAGER, new PoolingHttpClientConnectionManager(registry));
                client.property(GingerClientProperties.SYNC_CONNECTOR_PROVIDER, new ApacheConnectorProvider());
            } catch (Exception ex) {
                throw new RuntimeException(ex);
            }

        }
        return client;
    }

    public static Client attachProductionOutboundProxy(Client client) {
            client.property(ClientProperties.PROXY_URI, PRODUCTION_OUTBOUND_PROXY_ENDPOINT);
            client.property(ClientProperties.CONNECT_TIMEOUT, 5 * 1000);
            client.property(ClientProperties.READ_TIMEOUT, 120 * 1000);
//            // do not use HttpUrlConnectorProvider here because it has something wrong about proxy
            client.property(GingerClientProperties.SYNC_CONNECTOR_PROVIDER, new ApacheConnectorProvider());

        return client;
    }

    private static Client createNewGingerClient(String clientKey) {
        Configuration config = GingerConfigurationBuilder.newConfig(clientKey, "urn:REST:" + clientKey);
        return GingerClientBuilder.newClient(config);
    }

    private static Client addGingerClientDefaultSettings(Client client) {
        client.property(ClientProperties.CONNECT_TIMEOUT, 2000);
        client.property(ClientProperties.READ_TIMEOUT, 20000);

        client.property(ClientProperties.ASYNC_THREADPOOL_SIZE, JaxrsClientConfiguratorDefault.ASYNC_THREAD_POOL_SIZE_DEFAULT);
        client.property(GingerClientProperties.CORE_SIZE, JaxrsClientConfiguratorDefault.CORE_SIZE_DEFAULT);
        client.property(GingerClientProperties.QUEUE_SIZE, JaxrsClientConfiguratorDefault.QUEUE_SIZE_DEFAULT);

        client.property(GingerClientProperties.MAX_RETRY_COUNT, JaxrsClientConfiguratorDefault.MAX_RETRY_COUNT_DEFAULT);
        client.property(GingerClientProperties.HYSTRIX_ENABLED, JaxrsClientConfiguratorDefault.HYSTRIX_ENABLED_DEFAULT);

        client.property(GingerClientLoggingConstants.TRACE_ENABLED, false);

        client.property(GingerClientProperties.COS_SCOPES, "");
        // For application created with COS service profile, authorization header will automatically populate to all COS ginger clients.
        // To disable this feature, mark the ginger client is non-COS client by adding a property: company.cos.enabled=false
        client.property("company.cos.enabled", "false");

        // do not use ApacheConnectorProvider here because it has a bug about content-length when the requests have body.
        // bug summary: it will use its own Entity which always return content-length=-1.
        // so it will make ginger client (jersey) not setting "Content-Length" header, which is forbidden by most services.
        try {
            SSLContext sc = SSLContext.getInstance("SSL");
            sc.init(null, SSLUtil.getTrustAllCert(), new java.security.SecureRandom());
            HttpsURLConnection.setDefaultSSLSocketFactory(sc.getSocketFactory());
            HttpsURLConnection.setDefaultHostnameVerifier(SSLUtil.getTrustAllHostname());
        } catch (Exception ex) {
            throw new RuntimeException(ex);
        }
        client.property(GingerClientProperties.SYNC_CONNECTOR_PROVIDER, new HttpUrlConnectorProvider());
        client.property(GingerClientProperties.ASYNC_CONNECTOR_PROVIDER, new HttpUrlConnectorProvider());

        return client;
    }

    private static Client addJsonSettings(Client client) {
        client.register(new ObjectMapperProvider());
        return client;
    }
}
