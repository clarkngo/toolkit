function expandShadowRoots(node) {
    let nodesToExpand = [node];
    let allLinks = [];
  
    while (nodesToExpand.length > 0) {
      let currentNode = nodesToExpand.shift();
      if (currentNode.shadowRoot) {
        let shadowRoot = currentNode.shadowRoot;
        nodesToExpand = nodesToExpand.concat(Array.from(shadowRoot.querySelectorAll('*')));
        let links = shadowRoot.querySelectorAll('a[href*="/home/"]');
        allLinks = allLinks.concat(Array.from(links));
      } else if (currentNode.children) {
        nodesToExpand = nodesToExpand.concat(Array.from(currentNode.children));
      }
    }
  
    return allLinks.map(link => ({href: link.href, text: link.textContent.trim()}));
  }
  
  return expandShadowRoots(document);
  