# Backend Update Integration Files

## 📁 Files in this Directory

1. **update.controller.ts** - NestJS controller for update endpoints
2. **update.module.ts** - NestJS module definition
3. **README.md** - This file

## 🚀 Quick Setup

### 1. Create Update Module

```bash
cd ../4paws-backend
nest g module update
```

### 2. Copy Files

```bash
# From 4paws-agent directory
cp backend-integration/update.controller.ts ../4paws-backend/src/update/
cp backend-integration/update.module.ts ../4paws-backend/src/update/
```

### 3. Update App Module

Edit `src/app.module.ts`:
```typescript
import { UpdateModule } from './update/update.module';

@Module({
  imports: [
    // ... your existing modules
    UpdateModule, // Add this
  ],
})
export class AppModule {}
```

### 4. Add Environment Variable

Add to `.env`:
```env
AGENT_URL=http://localhost:5000
```

### 5. Test Endpoints

```bash
# Start backend
npm run start:dev

# Test in another terminal
curl http://localhost:3200/update/check
curl -X POST http://localhost:3200/update/start
curl http://localhost:3200/update/status
```

## 📡 API Endpoints

### GET /update/check

Check for available updates from agent.

**Response:**
```json
{
  "success": true,
  "current": {
    "frontend": "0.0.1",
    "backend": "0.0.1"
  },
  "latest": {
    "frontend": "0.0.2",
    "backend": "0.0.2"
  },
  "has_update": true,
  "details": {
    "frontend": {
      "current": "0.0.1",
      "latest": "0.0.2",
      "has_update": true
    },
    "backend": {
      "current": "0.0.1",
      "latest": "0.0.2",
      "has_update": true
    }
  }
}
```

### POST /update/start

Start the update process.

**Response:**
```json
{
  "success": true,
  "message": "Update started",
  "websocket_channel": "update_progress"
}
```

### GET /update/status

Get current version information.

**Response:**
```json
{
  "success": true,
  "versions": {
    "frontend": {
      "version": "0.0.1",
      "updated_at": "2025-10-04T10:00:00"
    },
    "backend": {
      "version": "0.0.1",
      "updated_at": "2025-10-04T10:00:00"
    }
  }
}
```

## 🔧 Configuration

### Environment Variables

```env
# Required
AGENT_URL=http://localhost:5000

# Optional - if agent runs on different host
# AGENT_URL=http://192.168.1.100:5000
```

### CORS Settings

If frontend runs on different domain, make sure CORS is configured:

```typescript
// main.ts
app.enableCors({
  origin: ['http://localhost:3100', 'your-frontend-domain'],
  credentials: true,
});
```

## 🧪 Testing

### Manual Testing

```bash
# Check for updates
curl http://localhost:3200/update/check

# Start update (backend will restart)
curl -X POST http://localhost:3200/update/start \
  -H "Content-Type: application/json"

# Get version info
curl http://localhost:3200/update/status
```

### Integration Testing

```typescript
// update.controller.spec.ts
import { Test, TestingModule } from '@nestjs/testing';
import { UpdateController } from './update.controller';
import { ConfigService } from '@nestjs/config';

describe('UpdateController', () => {
  let controller: UpdateController;

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      controllers: [UpdateController],
      providers: [
        {
          provide: ConfigService,
          useValue: {
            get: jest.fn((key: string) => {
              if (key === 'AGENT_URL') return 'http://localhost:5000';
              return null;
            }),
          },
        },
      ],
    }).compile();

    controller = module.get<UpdateController>(UpdateController);
  });

  it('should be defined', () => {
    expect(controller).toBeDefined();
  });

  // Add more tests...
});
```

## 🛡️ Error Handling

The controller includes comprehensive error handling:

- **Service Unavailable (503)**: When agent is not running
- **Internal Server Error (500)**: When update fails
- **HTTP Exception**: With detailed error messages

Example error response:
```json
{
  "success": false,
  "error": "Agent not available",
  "message": "Connection refused",
  "statusCode": 503
}
```

## 🔐 Security Considerations

### 1. Add Authentication

```typescript
import { UseGuards } from '@nestjs/common';
import { JwtAuthGuard } from '../auth/jwt-auth.guard';

@Controller('update')
@UseGuards(JwtAuthGuard) // Add authentication
export class UpdateController {
  // ...
}
```

### 2. Add Authorization

```typescript
import { Roles } from '../auth/roles.decorator';
import { RolesGuard } from '../auth/roles.guard';

@Controller('update')
@UseGuards(JwtAuthGuard, RolesGuard)
export class UpdateController {
  
  @Post('start')
  @Roles('admin') // Only admins can start updates
  async startUpdate() {
    // ...
  }
}
```

### 3. Rate Limiting

```typescript
import { Throttle } from '@nestjs/throttler';

@Controller('update')
export class UpdateController {
  
  @Get('check')
  @Throttle(10, 60) // 10 requests per minute
  async checkUpdate() {
    // ...
  }
}
```

## 📊 Logging

Add logging for better monitoring:

```typescript
import { Logger } from '@nestjs/common';

export class UpdateController {
  private readonly logger = new Logger(UpdateController.name);

  @Post('start')
  async startUpdate() {
    this.logger.log('Update started by user');
    // ...
    this.logger.log('Update completed successfully');
  }
}
```

## 🎯 Features

- ✅ Proxy to agent endpoints
- ✅ Error handling
- ✅ Type-safe responses
- ✅ ConfigService integration
- ✅ Ready for authentication
- ✅ Ready for logging
- ✅ Ready for rate limiting

## 📦 Dependencies

```json
{
  "@nestjs/common": "^10.0.0",
  "@nestjs/config": "^3.0.0"
}
```

These should already be in your backend.

## 📝 Next Steps

1. ✅ Add authentication if needed
2. ✅ Add logging for monitoring
3. ✅ Add rate limiting for protection
4. ✅ Add tests
5. ✅ Configure CORS if needed

## 📞 Need Help?

See the main `UPDATE_INTEGRATION_GUIDE.md` for complete documentation.

---

Happy coding! 🚀

