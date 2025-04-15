### Create an assets branch:

Store assets (such as images) in an assets branch which is detached from the main branch

```
git checkout --orphan assets
git reset --hard
cp /path/to/cat.png .
git add .
git commit -m 'Added cat picture'
git push -u origin assets
```

#### From
https://gist.github.com/mcroach/811c8308f4bd78570918844258841942