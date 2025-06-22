INSERT INTO payment_paymentmethod (created_at, updated_at, type, description, is_enabled) 
VALUES
    (NOW(), NOW(), 'credit_card', 'Credit Card', true),
    (NOW(), NOW(), 'bank_transfer', 'Bank Transfer', true);
