/**
 * Author: Justin Clayton
 */

'use strict';
(function() {
  $(document).ready(init);

  /** Initialize the JS to control page behavior. */
  function init() {
    setupBtns();
    $('#pw_confirm').on('input', onCheckPW);
  }

  /** Validate that pws match before sending to registration. */
  function onCheckPW() {
    if ($(this).val() === $('#pw').val()) {
      this.setCustomValidity('');
    } else {
      this.setCustomValidity('Passwords must match.');
    }
  }

  /** Swap to login/registration page. */
  function onSwapRegistration() {
    $('#register').toggleClass('hidden');
    $('#login').toggleClass('hidden');
  }

  /** Setup up buttons to swap between register and login. */
  function setupBtns() {
    $('#swap-login').click((e) => {
      e.preventDefault();
      onSwapRegistration();
    });
    $('#swap-registration').click((e) => {
      e.preventDefault();
      onSwapRegistration();
    });
  }
})();
