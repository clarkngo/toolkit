# Trust all certs
Resource: https://www.baeldung.com/okhttp-client-trust-all-certificates

HttpClientHelper.java
```
...
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
...
```

```
...
        try {
            SSLContext sc = SSLContext.getInstance("SSL");
            sc.init(null, SSLUtil.getTrustAllCert(), new java.security.SecureRandom());
            HttpsURLConnection.setDefaultSSLSocketFactory(sc.getSocketFactory());
            HttpsURLConnection.setDefaultHostnameVerifier(SSLUtil.getTrustAllHostname());
        } catch (Exception ex) {
            throw new RuntimeException(ex);
        }
...
```

SSLUtil.java
```
import javax.net.ssl.HostnameVerifier;
import javax.net.ssl.TrustManager;
import javax.net.ssl.X509TrustManager;

public class SSLUtil {
    public static HostnameVerifier getTrustAllHostname() {
        return (hostname, sslSession) -> true;
    }

    public static TrustManager[] getTrustAllCert() {
        return new TrustManager[]{
                new X509TrustManager() {
                    public java.security.cert.X509Certificate[] getAcceptedIssuers() {
                        return null;
                    }

                    public void checkClientTrusted(
                            java.security.cert.X509Certificate[] certs, String authType) {
                    }

                    public void checkServerTrusted(
                            java.security.cert.X509Certificate[] certs, String authType) {
                    }
                }
        };
    }
}
```
