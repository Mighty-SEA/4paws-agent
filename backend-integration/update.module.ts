/**
 * Update Module for 4Paws Backend
 * Place this in: src/update/update.module.ts
 */

import { Module } from '@nestjs/common';
import { UpdateController } from './update.controller';

@Module({
  controllers: [UpdateController],
  providers: [],
  exports: [],
})
export class UpdateModule {}

