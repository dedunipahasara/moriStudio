3dleebitMinho25!@


cute3d/
│
├── frontend/
│   │
│   ├── public/
│   │   ├── images/
│   │   ├── icons/
│   │   ├── models/
│   │   └── fonts/
│   │
│   ├── src/
│   │   │
│   │   ├── assets/
│   │   │   ├── images/
│   │   │   ├── icons/
│   │   │   └── styles/
│   │   │
│   │   ├── components/
│   │   │   ├── common/
│   │   │   ├── layout/
│   │   │   ├── forms/
│   │   │   ├── viewer/
│   │   │   ├── editor/
│   │   │   └── generation/
│   │   │
│   │   ├── features/
│   │   │   ├── auth/
│   │   │   ├── dashboard/
│   │   │   ├── generation/
│   │   │   ├── models/
│   │   │   ├── model-editor/
│   │   │   ├── gallery/
│   │   │   ├── profile/
│   │   │   └── settings/
│   │   │
│   │   ├── hooks/
│   │   ├── services/
│   │   ├── store/
│   │   ├── types/
│   │   ├── utils/
│   │   ├── constants/
│   │   ├── routes/
│   │   ├── pages/
│   │   ├── App.tsx
│   │   └── main.tsx
│   │
│   ├── .env
│   ├── .env.example
│   ├── package.json
│   ├── pnpm-lock.yaml
│   ├── tsconfig.json
│   └── vite.config.ts
│
│
├── backend/
│   │
│   ├── prisma/
│   │   ├── migrations/
│   │   │   └── 20261119075249_init/
│   │   │       └── migration.sql
│   │   │
│   │   └── schema.prisma
│   │
│   ├── src/
│   │   │
│   │   ├── config/
│   │   │   ├── prisma.ts
│   │   │   ├── env.ts
│   │   │   ├── cors.ts
│   │   │   ├── mail.ts
│   │   │   ├── storage.ts
│   │   │   └── queue.ts
│   │   │
│   │   ├── modules/
│   │   │   │
│   │   │   ├── auth/
│   │   │   │   ├── auth.routes.ts
│   │   │   │   ├── auth.controller.ts
│   │   │   │   ├── auth.service.ts
│   │   │   │   ├── auth.validation.ts
│   │   │   │   └── auth.types.ts
│   │   │
│   │   │   ├── password/
│   │   │   │   ├── password.routes.ts
│   │   │   │   ├── password.controller.ts
│   │   │   │   ├── password.service.ts
│   │   │   │   ├── password.validation.ts
│   │   │   │   └── password.types.ts
│   │   │
│   │   │   ├── email-verification/
│   │   │   │   ├── verification.routes.ts
│   │   │   │   ├── verification.controller.ts
│   │   │   │   ├── verification.service.ts
│   │   │   │   └── verification.types.ts
│   │   │
│   │   │   ├── users/
│   │   │   │   ├── user.routes.ts
│   │   │   │   ├── user.controller.ts
│   │   │   │   ├── user.service.ts
│   │   │   │   └── user.validation.ts
│   │   │
│   │   │   ├── generations/
│   │   │   │   ├── generation.routes.ts
│   │   │   │   ├── generation.controller.ts
│   │   │   │   ├── generation.service.ts
│   │   │   │   ├── generation.validation.ts
│   │   │   │   ├── generation.types.ts
│   │   │   │   └── generation.queue.ts
│   │   │
│   │   │   ├── models/
│   │   │   │   ├── model.routes.ts
│   │   │   │   ├── model.controller.ts
│   │   │   │   ├── model.service.ts
│   │   │   │   └── model.validation.ts
│   │   │
│   │   │   ├── assets/
│   │   │   │   ├── asset.routes.ts
│   │   │   │   ├── asset.controller.ts
│   │   │   │   ├── asset.service.ts
│   │   │   │   └── asset.validation.ts
│   │   │
│   │   │   └── uploads/
│   │   │       ├── upload.routes.ts
│   │   │       ├── upload.controller.ts
│   │   │       ├── upload.service.ts
│   │   │       └── upload.validation.ts
│   │   │
│   │   ├── integrations/
│   │   │   └── email/
│   │   │       ├── email.client.ts
│   │   │       ├── email.service.ts
│   │   │       └── email.types.ts
│   │   │
│   │   ├── workers/
│   │   │   ├── generation.worker.ts
│   │   │   └── generation.processor.ts
│   │   │
│   │   ├── templates/
│   │   │   └── emails/
│   │   │       ├── welcome-email.html
│   │   │       ├── verify-email.html
│   │   │       ├── forgot-password.html
│   │   │       ├── password-reset-success.html
│   │   │       └── password-changed-alert.html
│   │   │
│   │   ├── middleware/
│   │   │   ├── auth.middleware.ts
│   │   │   ├── error.middleware.ts
│   │   │   ├── validation.middleware.ts
│   │   │   └── rate-limit.middleware.ts
│   │   │
│   │   ├── utils/
│   │   │   ├── api-response.ts
│   │   │   ├── app-error.ts
│   │   │   ├── password.ts
│   │   │   ├── jwt.ts
│   │   │   ├── token.ts
│   │   │   ├── email.ts
│   │   │   └── logger.ts
│   │   │
│   │   ├── types/
│   │   │   └── express.d.ts
│   │   │
│   │   ├── app.ts
│   │   └── server.ts
│   │
│   ├── storage/
│   │   ├── uploads/
│   │   │   ├── images/
│   │   │   └── references/
│   │   ├── models/
│   │   ├── previews/
│   │   ├── thumbnails/
│   │   └── temp/
│   │
│   ├── tests/
│   │   ├── auth/
│   │   ├── password/
│   │   ├── email-verification/
│   │   ├── users/
│   │   ├── generations/
│   │   ├── models/
│   │   └── assets/
│   │
│   ├── .env
│   ├── .env.example
│   ├── .gitignore
│   ├── package.json
│   ├── pnpm-lock.yaml
│   └── tsconfig.json
│
│
|ai-engine/
│
├── app/
│   ├── main.py
│   ├── dependencies.py
│   │
│   ├── api/
│   │   ├── routes/
│   │   │   ├── health_routes.py
│   │   │   ├── generation_routes.py
│   │   │   ├── training_routes.py
│   │   │   └── model_routes.py
│   │   │
│   │   └── schemas/
│   │       ├── generation_schema.py
│   │       ├── training_schema.py
│   │       └── model_schema.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   ├── exceptions.py
│   │   └── logging.py
│   │
│   ├── ai/
│   │   │
│   │   ├── neural_networks/
│   │   │   ├── encoder.py
│   │   │   ├── decoder.py
│   │   │   ├── transformer.py
│   │   │   ├── attention.py
│   │   │   ├── embeddings.py
│   │   │   └── image_generator.py
│   │   │
│   │   ├── text_processing/
│   │   │   ├── tokenizer.py
│   │   │   ├── vocabulary.py
│   │   │   ├── prompt_encoder.py
│   │   │   └── text_features.py
│   │   │
│   │   ├── image_processing/
│   │   │   ├── image_encoder.py
│   │   │   ├── image_decoder.py
│   │   │   ├── image_features.py
│   │   │   ├── image_preprocessing.py
│   │   │   └── image_postprocessing.py
│   │   │
│   │   ├── generation/
│   │   │   ├── noise_scheduler.py
│   │   │   ├── noise_generator.py
│   │   │   ├── diffusion_model.py
│   │   │   ├── denoising_network.py
│   │   │   └── sampling.py
│   │   │
│   │   ├── training/
│   │   │   ├── trainer.py
│   │   │   ├── dataset.py
│   │   │   ├── dataloader.py
│   │   │   ├── loss_functions.py
│   │   │   ├── optimizer.py
│   │   │   ├── scheduler.py
│   │   │   ├── checkpoint.py
│   │   │   └── evaluation.py
│   │   │
│   │   └── inference/
│   │       ├── inference_engine.py
│   │       ├── generation_engine.py
│   │       └── prediction.py
│   │
│   ├── pipelines/
│   │   ├── text_to_image.py
│   │   └── image_generation_pipeline.py
│   │
│   ├── services/
│   │   ├── generation_service.py
│   │   ├── training_service.py
│   │   ├── image_service.py
│   │   └── export_service.py
│   │
│   ├── processors/
│   │   ├── image_processing.py
│   │   ├── image_optimization.py
│   │   ├── image_resizing.py
│   │   └── image_export.py
│   │
│   ├── storage/
│   │   ├── dataset_storage.py
│   │   ├── checkpoint_storage.py
│   │   └── output_storage.py
│   │
│   └── utils/
│       ├── gpu_utils.py
│       ├── image_utils.py
│       ├── memory_utils.py
│       └── seed.py
│
├── datasets/
│   ├── raw/
│   ├── processed/
│   ├── annotations/
│   └── metadata/
│
├── training/
│   ├── configs/
│   ├── experiments/
│   ├── logs/
│   └── evaluation/
│
├── checkpoints/
│   ├── text_encoder/
│   └── image_generator/
│
├── outputs/
│   ├── images/
│   ├── thumbnails/
│   └── logs/
│
├── scripts/
│   ├── prepare_dataset.py
│   ├── train_model.py
│   ├── evaluate_model.py
│   ├── generate_image.py
│   ├── check_gpu.py
│   └── export_image.py
│
├── tests/
│   ├── test_text_encoder.py
│   ├── test_image_processing.py
│   ├── test_diffusion_model.py
│   ├── test_training.py
│   └── test_generation.py
│
├── requirements.txt
├── pyproject.toml
├── .env.example
└── README.md
├── shared/
│   ├── contracts/
│   │   ├── api-types.ts
│   │   ├── generation-status.ts
│   │   └── model-types.ts
│   │
│   └── constants/
│       └── generation.ts
│
│
├── infrastructure/
│   ├── docker/
│   │   ├── backend.Dockerfile
│   │   └── ai-engine.Dockerfile
│   │
│   ├── scripts/
│   │   ├── start-dev.sh
│   │   ├── start-ai.sh
│   │   └── check-environment.sh
│   │
│   └── docker-compose.yml
│
│
├── docs/
│   ├── architecture.md
│   ├── ai-architecture.md
│   ├── ai-training-guide.md
│   ├── generation-pipeline.md
│   ├── api-documentation.md
│   ├── database-design.md
│   └── setup-guide.md
│
│
├── .gitignore
└── README.md
