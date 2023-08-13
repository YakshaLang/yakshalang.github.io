# New website structure

* Author: Bhathiya Perera

## Website

I have been working hard on updating the website infrastructure. New local PDF building feature is going to come in handy for downloadable documentation builds.
Additionally, (b)log section will be used for any updates.


## New `sr` string feature

This is going to help avoid copying and freeing strings by simply referencing these strings. However, note that `sr` can hold references to both statically allocated string literals and to dynamically allocated strings. Statically allocated strings will also store fixed length of the underlying string.

If you delete an `sr` it will delete underlying string (except when it is a statically allocated string (literal)).


## More features to come!

I have been writing new features I want to add as YAMA articles. Now they are in the same website and can be easily accessed.

## CSS

Ha! CSS is hard. Very hard. Perhaps I should have used some prebuilt theme.

## Docbox

Now this is moved into the website package itself.

