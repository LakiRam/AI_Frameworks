const express = require('express');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const { body, validationResult } = require('express-validator');

const router = express.Router();

let cachedPasswordSource;
let cachedPasswordHash;

const getConfiguredPasswordHash = async () => {
  const configuredPassword = process.env.USER_PASSWORD || 'admin123';

  if (!cachedPasswordHash || cachedPasswordSource !== configuredPassword) {
    cachedPasswordSource = configuredPassword;
    cachedPasswordHash = await bcrypt.hash(configuredPassword, 10);
  }

  return cachedPasswordHash;
};

router.post(
  '/login',
  [
    body('username').trim().notEmpty().withMessage('username is required.'),
    body('password').isString().notEmpty().withMessage('password is required.')
  ],
  async (req, res, next) => {
    try {
      const errors = validationResult(req);

      if (!errors.isEmpty()) {
        return res.status(400).json({
          errors: errors.array()
        });
      }

      const { username, password } = req.body;
      const configuredUsername = process.env.USER_USERNAME || 'admin';
      const passwordHash = await getConfiguredPasswordHash();
      const isValidPassword = await bcrypt.compare(password, passwordHash);

      if (username !== configuredUsername || !isValidPassword) {
        return res.status(401).json({
          message: 'Invalid username or password.'
        });
      }

      const user = {
        id: 1,
        username: configuredUsername
      };

      const token = jwt.sign(user, process.env.JWT_SECRET || 'development-jwt-secret', {
        expiresIn: process.env.JWT_EXPIRES_IN || '24h'
      });

      return res.json({
        token,
        user
      });
    } catch (error) {
      return next(error);
    }
  }
);

module.exports = router;
