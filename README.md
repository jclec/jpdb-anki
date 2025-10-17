# misc jpdb scripts

## delete non-new items in deck (jank approach)

Delete all non-new items in current deck view

- use jpdb's filters (e.g. known, failed) to filter words by status before running in console

```js
vocabList = document.querySelector(".vocabulary-list").children;
for (let item of vocabList) {
	if (item.className.includes("new")) continue;
	// select ellipsis (...) dropdown menu for card
	let dropdown = item.children[1].children[0].children[0]
		.children[0].children[1].children[0].children;
	// click "Remove", always at bottom of dropdown
	dropdown[dropdown.length - 1].children[0].children[3].click();
}
```
