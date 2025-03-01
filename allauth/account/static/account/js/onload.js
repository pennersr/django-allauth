(function () {
  document.addEventListener('DOMContentLoaded', function () {
    Array.from(document.querySelectorAll('script[data-allauth-onload]')).forEach(scriptElt => {
      const funcRef = scriptElt.dataset.allauthOnload
      if (typeof funcRef === 'string' && funcRef.startsWith('allauth.')) {
        const funcArg = JSON.parse(scriptElt.textContent)
        const func = funcRef.split('.').reduce((acc, part) => acc && acc[part], window)
        func(funcArg)
      }
    })
  })
})()
