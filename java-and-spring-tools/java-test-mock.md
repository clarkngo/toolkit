### UnneccessaryStubbingException fix at class level
```
@MockitoSettings(strictness = Strictness.LENIENT)
```


### SAMPLE
```
import lombok.extern.slf4j.Slf4j;
import org.json.JSONArray;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.boot.test.context.SpringBootTest;
import org.mockito.Mockito;
import org.springframework.test.util.ReflectionTestUtils;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.spy;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;


@Slf4j
@ExtendWith(MockitoExtension.class)
@SpringBootTest
public class HomeClickTest {
    HomeClick HSClickeSvc = new HomeClick();
    HomeClick spyHClickSvc = spy(HSClickeSvc);

    @Mock
    EsService mockEsService;

    @Mock
    MyResource mockMyResource;

    @Test
    public void testGetTopVariantTraffic_handlesNullInputs() {
        Long hour = 24*60*60L;
        JSONArray mockQueryResult = new JSONArray();
        JSONArray mockResult = new JSONArray();
        String logQL = String.format("topk(%s,sum(count_over_time({_namespace_=\"myapp\",_schema_=\"all\"}[24h]|logfmt))by(AlgorithmFamily,AlgorithmVariant))", 50);
        ReflectionTestUtils.setField(spyHClickSvc, "esService", mockEsService);
        ReflectionTestUtils.setField(spyHClickSvc, "sheResource", mockMyResource);
        when(spyHClickSvc.esService.index(anyString(), any(JSONArray.class))).thenReturn(null);
        when(spyHClickSvc.sheResource.runLogQLQuery(anyString(), anyString(), anyString(), anyString())).thenReturn(mockQueryResult);
        when(spyHClickSvc.sheResource.timeDiffSeconds(anyString(), anyString())).thenReturn(hour);
        when(spyHClickSvc.getAlgoTrafficResponse(any(JSONArray.class))).thenReturn(mockResult);

        spyHClickSvc.getTopStat(null, null, null, "0");

        verify(spyHClickSvc.sheResource).timeDiffSeconds(anyString(), anyString());
        verify(spyHClickSvc.sheResource).runLogQLQuery(anyString(), anyString(), eq(Long.toString(hour + 1l)), eq(logQL));
        verify(spyHClickSvc).getTopStat(null, null, null, "0");
        verify(spyHClickSvc).getStatResponse(mockQueryResult);
        verify(spyHClickSvc.esService, Mockito.never()).index(anyString(), any(Object.class));

        spyHClickSvc.getTopStat(null, null, null, "1");
        verify(spyHClickSvc.esService).index(anyString(), any(Object.class));
    }
}

```

another example
```
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import lombok.extern.slf4j.Slf4j;
import org.junit.Assert;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.util.ReflectionTestUtils;

import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.*;


@Slf4j
@ExtendWith(MockitoExtension.class)
@SpringBootTest
class MyResourceTest {

    MyResource myResource = new MyResource();
    MyResource spyMyResource = spy(myResource);

    @Mock
    MyService mockMyService;

    @Test
    void test() throws JsonProcessingException {
        String jsonString = "{\"offset\"}";
        Response mockResult = Util.getDefaultObjectMapper().readValue(jsonString, Response.class);
        ReflectionTestUtils.setField(spyMyResource, "myService", mockMyService);
        when(spyMyResource.myService.search(anyString(), anyString(), anyBoolean())).thenReturn(mockResult);
        log.info(spyMyResource.myMethod().toString());
        verify(spyMyResource).myMethod();
    }

}
```
