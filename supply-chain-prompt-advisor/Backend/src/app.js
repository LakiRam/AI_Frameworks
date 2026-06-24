require('dotenv').config();

const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const morgan = require('morgan');
const rateLimit = require('express-rate-limit');

const authRoutes = require('./routes/auth');
const recommendationRoutes = require('./routes/recommendations');
const healthRoutes = require('./routes/health');

const app = express();

const limiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 100,
  standardHeaders: true,
  legacyHeaders: false,
  message: {
    message: 'Too many requests, please try again later.'
  }
});

app.disable('x-powered-by');
app.use(helmet());
app.use(
  cors({
    origin: process.env.CORS_ORIGIN || 'http://localhost:3000'
  })
);
app.use(morgan('combined'));
app.use(express.json({ limit: '1mb' }));
app.use(limiter);

app.use('/api/auth', authRoutes);
app.use('/api', healthRoutes);
app.use('/api', recommendationRoutes);

app.use((req, res) => {
  res.status(404).json({
    message: 'Route not found.'
  });
});

app.use((err, req, res, next) => {
  const statusCode = err.statusCode || 500;
  const message = err.message || 'Internal server error.';

  if (statusCode >= 500) {
    console.error(err);
  }

  res.status(statusCode).json({
    message
  });
});

module.exports = app;
