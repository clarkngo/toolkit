
Already have rsa public key added to github but still has error:
```
Host key verification failed.
fatal: Could not read from remote repository.
```

Solution:
```
ssh-keyscan -t rsa github.com >> ~/.ssh/known_hosts
```
