$(document).ready(function() {
	const urlParams = new URLSearchParams(window.location.search);
	let order_id= urlParams.get('order_id');
	updatePaymentRequestdetails(order_id)
	
	$('#orderId').val(order_id).prop('disabled', true);

	function updatePaymentRequestdetails(){
		frappe.call({
			method: "payments.templates.pages.make_payment.get_payment_details",
			freeze: true,
			headers: {
				"X-Requested-With": "XMLHttpRequest"
			},
			args: {
				"order_id": order_id
			},
			callback: function(r) {
				if (r.message.length) {
					$('#amount').val(r.message[0].amount).prop('disabled', true);
					makePaymentButton(r.message)
				}
				else{
					showInvalidOrderMessage(order_id)
				}
			}
		})
	}

	function showInvalidOrderMessage(order_id) {
		$('#button-group').html(`
			<div class="error-message-container">
				<h2 class="error-title">Invalid Order ID</h2>
				<p class="error-description">The Order ID "<span class="order-id">${order_id || "N/A"}</span>" is not valid.</p>
				<p>Please enter a valid order ID to proceed with the payment.</p>
			</div>
		`);
   }

   function makePaymentButton(payment_options) {
		// const $buttonContainer = $('#button-group');

		// payment_options.forEach(({ payment_label, payment_url, icon }) => {
		// 	const label = payment_label.toLowerCase();
		// 	const $button = $(`
		// 		<button 
		// 			class="payment-button ${label}" 
		// 			data-url="${payment_url || ''}" 
		// 			${!payment_url ? 'disabled title="Payment Option is not enabled"' : ''}>
		// 			<img src=${icon} alt= "Pay with ${payment_label}" class="button-icon" />
		// 		</button>
		// 	`);			

		// 	$button.on('click', function (event) {
		// 		event.preventDefault();
		// 		const url = $(this).data('url');
		// 		if (url) location.assign(url);
		// 	});

		// 	$buttonContainer.append($button);
		// });
		const $buttonContainer = $('#button-group');

		payment_options.forEach(({ payment_label, payment_url = '', icon = 'default-icon.png' }) => {
			const label = payment_label.toLowerCase();
			const isDisabled = !payment_url;
			// const cardHtml = `
			// 	<div class="payment-card ${isDisabled ? 'disabled' : ''}">
			// 		<div class="card-content">
			// 			<div class="img-container">
			// 				<img 
			// 					src="${icon}" 
			// 					alt="Pay with ${payment_label}" 
			// 					class="card-icon" 
			// 					loading="lazy"
			// 				/>
			// 			</div>
			// 			<button 
			// 				class="card-button" 
			// 				data-url="${payment_url}" 
			// 				${isDisabled ? 'disabled aria-disabled="true" title="Payment option not enabled"' : ''}>
			// 				${isDisabled ? 'Unavailable' : 'Pay Now'}
			// 			</button>
			// 		</div>
			// 	</div>
			// `;

			const cardHtml = `
				<div class="payment-card ${isDisabled ? 'disabled' : ''}">
					<div class="img-container">
						<img 
							src="${icon}" 
							alt="Pay with ${payment_label}"
							class="card-icon" 
							loading="lazy"
						/>
					</div>
					<button 
						class="card-button" 
						data-url="${payment_url}" 
						${isDisabled ? 'disabled aria-disabled="true" title="Payment option not enabled"' : ''}>
						${isDisabled ? 'Unavailable' : 'Pay Now'}
					</button>
				</div>
			`;


			const $card = $(cardHtml);

			if (!isDisabled) {
				$card.find('.card-button').on('click', function (event) {
					event.preventDefault();
					const url = $(this).data('url');
					if (url) {
						location.assign(url);
					}
				});
			}

			$buttonContainer.append($card);
		});


	}
});