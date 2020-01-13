
// Set your publishable key: remember to change this to your live publishable key in production
// See your keys here: https://dashboard.stripe.com/account/apikeys

var stripe = Stripe('pk_test_Yefm4kQnlPKSvM5W6BW24gk700SThCTQkg');
var elements = stripe.elements();

// Set up Stripe.js and Elements to use in checkout form -- *Once loaded*

  console.log('loading static files');
  // console.log('subscription' + {{ subscription }});

  var style = {
    base: {
      color: "#32325d",
      fontFamily: '"Helvetica Neue", Helvetica, sans-serif',
      fontSmoothing: "antialiased",
      fontSize: "16px",
      "::placeholder": {
        color: "#aab7c4"
      }
    },
    invalid: {
      color: "#fa755a",
      iconColor: "#fa755a"
    }
  };

  var cardElement = elements.create("card", { style: style });
  cardElement.mount("#card-element");


  // Event listener for validation

  cardElement.addEventListener('change', function(event) {
    var displayError = document.getElementById('card-errors');
    if (event.error) {
      displayError.textContent = event.error.message;
    } else {
      displayError.textContent = '';
    }
  });


  var submit = document.getElementById('submit');

  //On submit payment information
  $(submit).on("click", function(){
      console.log('Submitted subscription form');

      //Code for what happens on submit goes here.
      stripe.createPaymentMethod({
        type: 'card',
        card: cardElement,
        billing_details: {
          email: email,
        },
      }).then(function(result) {

        // Handle result.error or result.paymentMethod
        if(result.error){

        }else if(result.paymentMethod){
            fetch('stripe-api-create-customer/', {
                method: 'post',
                csrf_token: csrf_token,
                headers: {
                  'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                      // Using request.user.email by default on server-side
                      // email: '{{ request.user.email }}',
                      payment_method: result.paymentMethod
                      })
            }).then(response => {
                return response.json();
            }).then(customer => {
                    // The customer has been created
                    
                      //Update user, if error in server-side code, display the error, else success message

                      const { latest_invoice } = subscription;
                      const { payment_intent } = latest_invoice;

                      if (payment_intent) {
                        const { client_secret, status } = payment_intent;

                        if (status === 'requires_action') {
                            stripe.confirmCardPayment(client_secret).then(function(result) {
                                if (result.error) {
                                  // Display error message in your UI.
                                  // The card was declined (i.e. insufficient funds, card has expired, etc)
                                  displayError = document.getElementById('card-errors');
                                  displayError.textContent = "The card was declined. Reason: " + result.error.message;
                                } else {
                                  // Show a success message to your customer
                                    toastr.success("Subscription created succesfully!");
                                }
                            });
                        } else {
                          // No additional information was needed
                          // Show a success message to your customer
                          toastr.success("Subscription created succesfully!");
                        }
                     }
                   }
            });
        }
      });
  });
