### Adding environment variable
Let's say you have the following in application-Dev.properites and you have the test to get env property and values.

`application-Dev.properties`
```
my.required-property=${MY_VARIABLE}
```

In your test class
```
@TestPropertySource(properties = {
        "MY_VARIABLE=myVariable"
})
```
