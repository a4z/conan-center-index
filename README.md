# Our fork of the CCI

This is our version the the conan-center-index

We (currently) do not want to run our own version of the cci, since this would mean to lose all upstream changes.
And they are often very valuable.

But we might have to do some adoptions to some recipes, or in case or changes suggested upstream, we do not want to wait until they got merged.
In both cases

To get changes from upstream into this repo checkout this repo, add upstream as remote, pull master from upstream and merge it into the nsdk branch of this repo.

This is why there is only the nsdk branch in this repo.

