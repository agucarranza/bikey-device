#include <linux/module.h>   
#include <linux/string.h>    
#include <linux/fs.h>      
#include <linux/uaccess.h>
#include <linux/init.h>
#include <linux/cdev.h>

#include <linux/device.h>
#include <linux/kernel.h>
#include <linux/errno.h>
#include <linux/io.h>
#include <linux/sched.h>
#include <linux/interrupt.h>

#include <linux/list.h>
#include <linux/irq.h>
#include <linux/slab.h>
#include <linux/gpio.h>
#include <linux/time.h>
#include <linux/delay.h>

#include <linux/gpio.h>

#define LED0 22

static dev_t first; 		// Global variable for the first device number
static struct cdev c_dev; 	// Global variable for the character device structure
static struct class *cl; 	// Global variable for the device class

static char   *msg=NULL;

static int my_open(struct inode *i, struct file *f)
{
    printk(KERN_INFO "Bikey: open()\n");
    return 0;
}
static int my_close(struct inode *i, struct file *f)
{
    printk(KERN_INFO "Bikey: close()\n");
    return 0;
}


static ssize_t my_read(struct file *f, char __user *buf, size_t len, loff_t *off)
{
	char led_value;
	short count;
    printk(KERN_INFO "Bikey: read()\n");

    led_value = gpio_get_value(LED0);
	msg[0] = led_value;
	len = 1;
	count = copy_to_user(buf, msg, len);
	printk("GPIO%d=%d\n",LED0 ,gpio_get_value(LED0));
 
    return 0;
}

static ssize_t my_write(struct file *f, const char __user *buf, size_t len, loff_t *off)
{
    short count;

    printk(KERN_INFO "Bikey: write()\n");

    memset(msg, 0, 32);
    count = copy_from_user(msg, buf, len);

    if (msg[0]=='1') {
		gpio_set_value(LED0, 1);     // LED0 ON
	} 
	else if (msg[0]=='0') {
		gpio_set_value(LED0, 0);     // LED0 OFF
	}  
	else 
		printk("Unknown command , 1 or 0 \n");

    return len;
}

static struct file_operations pugs_fops =
{
    .owner = THIS_MODULE,
    .open = my_open,
    .release = my_close,
    .read = my_read,
    .write = my_write
};

static int __init bikey_init(void) /* Constructor */
{
    int ret;
    struct device *dev_ret;

    msg = (char *)kmalloc(32, GFP_KERNEL);
	if (msg !=NULL)
		printk("malloc allocator address: 0x%p\n", msg);

    printk(KERN_INFO "Bikey: Registrado exitosamente..!!\n");

    if ((ret = alloc_chrdev_region(&first, 0, 1, "Bikey")) < 0)
    {
        return ret;
    }

    if (IS_ERR(cl = class_create(THIS_MODULE, "SdeC_drive")))
    {
        unregister_chrdev_region(first, 1);
        return PTR_ERR(cl);
    }

    if (IS_ERR(dev_ret = device_create(cl, NULL, first, NULL, "Bikey")))
    {
        class_destroy(cl);
        unregister_chrdev_region(first, 1);
        return PTR_ERR(dev_ret);
    }

    cdev_init(&c_dev, &pugs_fops);
    if ((ret = cdev_add(&c_dev, first, 1)) < 0)
    {
        device_destroy(cl, first);
        class_destroy(cl);
        unregister_chrdev_region(first, 1);
        return ret;
    }

    if((int)gpio_is_valid(LED0) < 0) {
		printk("gpio %d is valid error \n", LED0);
		return -1;
	}

	if(gpio_request(LED0,"LED0_GPIO") < 0){
		printk("gpio %d is request error \n", LED0);
		return -1;
	}
	gpio_direction_output(LED0, 0);
    
    return 0;
}

static void __exit bikey_exit(void) /* Destructor */
{
	gpio_set_value(LED0,0);
	gpio_free(LED0);

    cdev_del(&c_dev);
    device_destroy(cl, first);
    class_destroy(cl);
    unregister_chrdev_region(first, 1);
    printk(KERN_INFO "Bikey: adios!\n");
}

module_init(bikey_init);
module_exit(bikey_exit);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Grupo 5 SisComp 2020");
MODULE_DESCRIPTION("Driver GPIO para Bikey");