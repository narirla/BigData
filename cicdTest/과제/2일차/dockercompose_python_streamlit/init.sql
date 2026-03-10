CREATE TABLE product (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    price DECIMAL(10, 2)
);

INSERT INTO product (name, price) VALUES ('Product 1', 10.99);
INSERT INTO product (name, price) VALUES ('Product 2', 15.49);
INSERT INTO product (name, price) VALUES ('Product 3', 20.00);
