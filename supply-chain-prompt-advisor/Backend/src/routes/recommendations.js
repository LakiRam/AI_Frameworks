const express = require('express');
const { body, validationResult } = require('express-validator');

const auth = require('../middleware/auth');
const scenarios = require('../data/scenarios');
const { SUPPORTED_PROVIDERS, generateRecommendations } = require('../providers');

const router = express.Router();
const supportedDomains = Object.keys(scenarios);
const supportedProviderIds = SUPPORTED_PROVIDERS.map((provider) => provider.id);

const recommendationValidation = [
  body('domain')
    .isString()
    .trim()
    .isIn(supportedDomains)
    .withMessage(`domain must be one of: ${supportedDomains.join(', ')}`),
  body('scenario')
    .isString()
    .trim()
    .notEmpty()
    .isLength({ max: 4000 })
    .withMessage('scenario is required and must be at most 4000 characters.'),
  body('context')
    .optional({ nullable: true })
    .isString()
    .isLength({ max: 4000 })
    .withMessage('context must be a string up to 4000 characters.'),
  body('llmProvider')
    .isString()
    .trim()
    .isIn(supportedProviderIds)
    .withMessage(`llmProvider must be one of: ${supportedProviderIds.join(', ')}`),
  body('llmConfig').isObject().withMessage('llmConfig must be an object.'),
  body('llmConfig.apiKey')
    .isString()
    .trim()
    .notEmpty()
    .withMessage('llmConfig.apiKey is required.'),
  body('llmConfig.endpoint')
    .optional({ nullable: true })
    .isString()
    .trim()
    .withMessage('llmConfig.endpoint must be a string when provided.'),
  body('llmConfig.model')
    .optional({ nullable: true })
    .isString()
    .trim()
    .withMessage('llmConfig.model must be a string when provided.'),
  body().custom((value) => {
    if (value.llmProvider === 'azure-openai' && !value?.llmConfig?.endpoint) {
      throw new Error('llmConfig.endpoint is required for azure-openai.');
    }

    return true;
  })
];

router.post('/recommendations', auth, recommendationValidation, async (req, res, next) => {
  try {
    const errors = validationResult(req);

    if (!errors.isEmpty()) {
      return res.status(400).json({
        errors: errors.array()
      });
    }

    const { domain, scenario, context, llmProvider, llmConfig } = req.body;
    const recommendations = await generateRecommendations({
      llmProvider,
      llmConfig,
      domain,
      scenario,
      context,
      domainMetadata: scenarios[domain]
    });

    return res.json({
      recommendations,
      domain,
      scenario
    });
  } catch (error) {
    error.statusCode = error.statusCode || 500;
    error.message = `Failed to generate recommendations: ${error.message}`;
    return next(error);
  }
});

router.get('/providers', (req, res) => {
  res.json({
    providers: SUPPORTED_PROVIDERS
  });
});

module.exports = router;
