# Skraeppex: The Extraction Language

**This section is for the experienced user.**

Skraeppex is a declarative extraction specification language. The syntax looks a lot like Yaml, but *it is not.* 

Each line of Skraeppex specifies something to extract. A simple top-level  statement can be an identifier followed 
by a css selector:

```
name: .text-heading-xlarge
```
This will extract all text nodes with the css selector `.text-heading-xlarge`. The nodes will be inserted in column `name` in the output csv file.

A lot of nodes will not be targeted with a simple statement. Then you will need a block statement. It can look like this:
```
-experience-box:
    selector: section.artdeco-card
    contains: Experience
```
This block defines  an `experience-box` defined by the `selector` field with the css selector value of `section.artdeco-card`  . It also has a filter field `contains`, that specifies that only nodes containing the string `"Experience"` should be included.

There's a minus sign before `experience-box`, and that means that there should be no column of that name in the output csv file. So right now, it doesn't generate any output. To fix that, we can add a field to the box:
```
-experience-box:
    selector: section.artdeco-card
    contains: Experience
    title: div.display-flex.flex-column > div
```
Now we have a simple field `title` in the block statement. This means that we are looking for an `experience-box`, defined by the given `selector`, but only if it contains the string `Experience`. If that is the case, we want to extract the `title` nodes, given by the css selector `div.display-flex.flex-column > div`.

We can nest block statements in block statements, like this:

```
name: .text-heading-xlarge
-experience-box:
    selector: section.artdeco-card
    contains: Erfaring
    -experience-item: 
        selector: div
        -core-info:
            selector: div.justify-space-between
            title: div.display-flex.flex-column > div
            employer: div.full-width > span:nth-child(2)
            duration: div > span:nth-child(3)
            -compound-block-items: 
                selector: a.display-flex
                employer: [data-field='logo']
                duration: contains! From
                title: 
                    selector: span.visually-hidden
                    nodes: 1
```
The `experience-item` block will now look inside the text nodes of `experience-box`. *It's a smaller lasso inside a 
bigger lasso.*

A block statement can reuse field identifiers, such as `title` above here. This means that nodes will be placed in 
the same column `title` in the csv output file.

Inside a block statement, it is also possible to use a string as selector, instead of a css selector, as 
in `duration: contains! From` , that will select nodes where the string `"From"` occurs.

Some selectors will find more than one node. In that case, the result will be represented 
as `<NODE 1>The first found node<NODE 2>The second...`, and so on. In that case, 
the `nodes` filter can specify which nodes to select, such as: `nodes: 1`, which selects 
the first node, or `nodes: 2, 4-5`, that selects nodes 2, 4 and 5, and so forth.

## Data wrangling

Skraeppex provides a few features for transforming the collected data. These are:

```
filldown: name, employer, title
dropna: yes
```

Filldown will copy the selected column values all the way down in the output, until a new value occurs. Dropna 
removes rows with blank cells.

In the example above, this will ensure correct semantics in the output. But HTML structure is complex, so it 
is important to check the correctness of the output.

It is also possible to user filters as `duration-start: before! -`, that will find the text before the hyphen.
`after!` works similar:

```
dur-start: before! -
dur-end: after! ·
```

Another feature is extraction by regular expressions:

```
-duration:
   selector: span
   contains: ·
   nodes: 1
   dur-start: regex! ^(.*?)\s-
   dur-end: regex! -\s(.*?)\s·
```
This will create two columns `dur-start` and `dur-end` in the output csv, with the strings extracted from the span element. 

