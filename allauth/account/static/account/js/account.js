(function () {
  const allauth = window.allauth = window.allauth || {}

  function manageEmailForm (o) {
    const actions = document.getElementsByName('action_remove')
    if (actions.length) {
      actions[0].addEventListener('click', function (e) {
        if (!window.confirm(o.i18n.confirmDelete)) {
          e.preventDefault()
        }
      })
    }
  }

  allauth.account = {
    forms: {
      manageEmailForm
    }
  }
})()
