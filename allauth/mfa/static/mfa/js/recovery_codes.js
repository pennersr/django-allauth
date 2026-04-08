(function () {
  const allauth = window.allauth = window.allauth || {}
  const warn = function (e) { e.preventDefault() }

  function viewForm (o) {
    const saveConfirmation = document.getElementById(o.ids.saveConfirmation)
    if (saveConfirmation) {
      window.addEventListener('beforeunload', warn)
      saveConfirmation.addEventListener('change', function () {
        if (this.checked) {
          window.removeEventListener('beforeunload', warn)
        } else {
          window.addEventListener('beforeunload', warn)
        }
      })
    }

    const textarea = document.getElementById(o.ids.recoveryCodes)
    if (textarea) {
      textarea.addEventListener('click', function (e) {
        e.target.select()
        if (navigator.clipboard) {
          navigator.clipboard.writeText(e.target.value).catch(function () {})
        }
      })
    }
  }

  allauth.recoveryCodes = {
    forms: {
      viewForm
    }
  }
})()
