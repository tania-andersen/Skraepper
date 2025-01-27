# Recipes

## Onthemarket.com

Page url template: 

```https://www.onthemarket.com/for-sale/property/camden/?page=*&view=map-list```

Detail page selector: 

```a[href^="/details/"]```

GDPR dialog: 

```https://www.onthemarket.com```

Skraeppex:
```
filldown: Title, Price, Beds
dropna: yes
-title-info:
   selector: head > title
   Title: regex! , \s*( .*? )\s *-
   Price: regex! -\s*( .* )
Beds:
   selector: div.leading-none.whitespace-nowrap
   nodes: 1
Baths:
   selector: div. leading-none.whitespace-nowrap
   nodes: 2
```



## Ebay

Page url template: 

```https://www.ebay.com/sch/i.html?_nkw=lenovo+thinkpad+x1+carbon&_sacat=0&_from=R40&_pgn=*```

Detail page selector: 

```div > div.s-item__info.clearfix > a```

Skraeppex:
```
Info: head > title
Condition: 
   selector: div > div:nth-child(1) > div:nth-child(2) > dl > dd > div > div > span
   nodes: 1
```



## Linkedin

Page url template: 

```https://www.linkedin.com/search/results/people/?keywords=Novo&origin=CLUSTER_EXPANSION&page=*```

Detail page selector: 

```div.t-roman.t-sans div.display-flex > span > span > a[data-test-app-aware-link][href*="linkedin.com/in/"]```

Login page: 

```https://www.linkedin.com/login/```

Success tokens: 

```Experience, results```

Skraeppex:
```
filldown: Name, Employer, Title
dropna: yes
Name: h1
-experience-box:
    selector: section.artdeco-card
    contains: Experience
    -experience-item:
        selector: div.display-flex.flex-row.justify-space-between > div
        -employer-container: 
           selector: div.display-flex.flex-row.justify-space-between > div > span:nth-child(2) > span:nth-child(1)
           Employer: regex! ^(.*?)(?:\s·.*)?$
        Title: div.display-flex.flex-row.justify-space-between > div > div > div > div > div
        -dur: 
           selector: div.display-flex.flex-column.align-self-center.flex-grow-1 > div.display-flex.flex-row.justify-space-between > div > span:nth-child(3) > span.pvs-entity__caption-wrapper
           Dur-start: regex! ^(.*?)\s-
           Dur-end: regex! (?<=- ).+?(?= ·)
    -compound: 
       selector: div.display-flex.flex-row.justify-space-between
       Employer:
          selector: a[data-field="experience_company_logo"].optional-action-target-wrapper.display-flex.flex-column.full-width > div
       -title-and-dur: 
          selector: a.optional-action-target-wrapper
          Title: 
             selector: div > div > div > div
             nodes: 1
          -dur-container:
             selector: a.optional-action-target-wrapper > span
             -duration: 
                 selector: span
                 contains: ·
                 nodes: 1
                 Dur-start: regex! ^(.*?)\s-
                 Dur-end: regex! (?<=- ).+?(?= ·)
```